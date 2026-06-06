#!/usr/bin/env python3
"""Python script health check: syntax, imports, hardcoded paths, import feasibility."""

import ast
import argparse
import importlib.util
import os
import re
import traceback
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Match Windows-style drive-letter paths like F:/foo/bar or C:\Users\...
# Negative lookahead for "?..." to avoid matching path-like query params.
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/](?!\?)")

# Subproject grouping rules: (needle_substring, label) — first match wins.
SUBPROJECT_RULES = [
    ("__init__.py",           "__init__"),
    ("sleep_classify",        "sleep_classify"),
    ("IMU_sleep_stage",       "sleep_stage/IMU_sleep_stage"),
    ("迁移标签代码",            "sleep_stage/迁移标签"),
    ("Sleep-pdf处理代码",      "sleep_stage/Sleep-pdf"),
    ("",                      "other"),  # catch-all fallback
]

MAX_SAMPLES = 5
TOP_N = 10


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Per-file health check result."""

    path: str = ""
    syntax_ok: bool = True
    syntax_error: Optional[str] = None
    read_error: Optional[str] = None
    imports: list[str] = field(default_factory=list)
    hardcoded_paths: list[str] = field(default_factory=list)
    comments_only: bool = False
    import_test: dict[str, str] = field(default_factory=dict)
    skipped_main: bool = False
    issue_type: str = ""


@dataclass
class Summary:
    """Aggregate statistics across all checked files."""

    total: int = 0
    syntax_failed: list[str] = field(default_factory=list)
    import_missing_top: list[tuple[str, int]] = field(default_factory=list)
    hardcoded_paths_files: list[str] = field(default_factory=list)
    by_subproject: dict[str, list[CheckResult]] = field(default_factory=dict)
    env_only_count: int = 0
    script_issue_count: int = 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Python 脚本可运行性体检")
    parser.add_argument(
        "workspace",
        nargs="?",
        default=".",
        help="工作区根目录（默认当前目录）",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    "master_study_env",
    ".idea",
    "__pycache__",
    ".git",
    ".opencode",
    "node_modules",
}


def discover_py_files(workspace: Path) -> list[Path]:
    """Recursively find all .py files under *workspace*, skipping known dirs."""
    files: list[Path] = []
    for root, dirs, _ in os.walk(workspace):
        root_path = Path(root)
        # Prune skip-dirs in-place so os.walk never descends into them
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for entry in os.listdir(root):
            if entry.endswith(".py"):
                files.append(root_path / entry)
    files.sort(key=lambda p: p.as_posix())
    return files



# ---------------------------------------------------------------------------
# Per-file health check
# ---------------------------------------------------------------------------

def check_file(path: Path) -> CheckResult:
    """Run all 5 check steps on a single .py file, return a CheckResult."""
    result = CheckResult()
    result.path = path.as_posix()

    # --- Read + Step 1: syntax check ---
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        result.syntax_ok = False
        result.read_error = f"{type(e).__name__}: {e}"
        return result

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        result.syntax_ok = False
        result.syntax_error = f"{e.msg} (line {e.lineno})"
        return result
    except UnicodeDecodeError as e:
        result.syntax_ok = False
        result.syntax_error = f"UnicodeDecodeError: {e}"
        return result

    # Steps 2-5 require a valid AST tree
    if tree is None:
        return result

    # --- Step 2: extract imports ---
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if not top.startswith("."):
                    imports.add(top)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None and not node.module.startswith("."):
                top = node.module.split(".")[0]
                imports.add(top)
    result.imports = sorted(imports)

    # --- Step 3: hardcoded path scan (AST strings) ---
    paths: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if WINDOWS_PATH_RE.search(node.value):
                paths.append(node.value.strip()[:120])
                if len(paths) >= MAX_SAMPLES:
                    break
    result.hardcoded_paths = paths

    # --- Step 3b: comment-only fallback ---
    if not imports and not paths:
        raw = path.read_text(encoding="utf-8", errors="replace")
        matches = list(WINDOWS_PATH_RE.finditer(raw))
        if matches:
            result.comments_only = True
            for m in matches[:MAX_SAMPLES]:
                start = max(0, m.start() - 10)
                end_idx = min(len(raw), m.end() + 60)
                result.hardcoded_paths.append(raw[start:end_idx].strip()[:120])

    # --- Step 4: import feasibility (find_spec, NOT import_module) ---
    for mod in result.imports:
        try:
            spec = importlib.util.find_spec(mod)
            result.import_test[mod] = "OK" if spec is not None else "MISSING"
        except Exception as e:
            tb_line = traceback.format_exception_only(type(e), e)[-1].strip()
            result.import_test[mod] = f"ERROR: {tb_line}"

    # --- Step 5: detect __main__ guard ---
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            left = node.test.left
            if isinstance(left, ast.Name) and left.id == "__name__":
                for op in node.test.ops:
                    if isinstance(op, (ast.Eq, ast.Is)):
                        result.skipped_main = True
                        break
                if result.skipped_main:
                    break

    return result


# ---------------------------------------------------------------------------
# Classification & summarization
# ---------------------------------------------------------------------------

def classify(r: CheckResult) -> str:
    """Classify a CheckResult into one of 5 issue types."""
    if r.comments_only:
        return "all-commented"
    if not r.syntax_ok:
        return "script-issue"
    has_script = bool(r.hardcoded_paths)
    has_env = any(v != "OK" for v in r.import_test.values())
    if has_env and has_script:
        return "mixed"
    if has_env:
        return "env-only"
    if has_script:
        return "script-issue"
    return "clean"


def subproject_of(path_str: str) -> str:
    """Assign a file to its subproject group using SUBPROJECT_RULES."""
    for needle, label in SUBPROJECT_RULES:
        if needle in path_str:
            return label
    return "other"


def summarize(results: list[CheckResult]) -> Summary:
    """Aggregate per-file results into a Summary."""
    missing_counter: Counter[str] = Counter()
    subprojects: dict[str, list[CheckResult]] = {}

    for r in results:
        r.issue_type = classify(r)

        sp = subproject_of(r.path)
        subprojects.setdefault(sp, []).append(r)

        # Collect missing modules for global ranking
        for mod, status in r.import_test.items():
            if status != "OK":
                missing_counter[mod] += 1

    summary = Summary()
    summary.total = len(results)
    summary.syntax_failed = [r.path for r in results if not r.syntax_ok]
    summary.hardcoded_paths_files = [r.path for r in results if r.hardcoded_paths]
    summary.by_subproject = subprojects
    summary.env_only_count = sum(1 for r in results if r.issue_type == "env-only")
    summary.script_issue_count = sum(
        1 for r in results if r.issue_type in ("script-issue", "all-commented", "mixed")
    )
    summary.import_missing_top = missing_counter.most_common(TOP_N)
    return summary



# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _icon(issue_type: str) -> str:
    return {"clean": "✅", "env-only": "✅", "all-commented": "⚠️",
            "mixed": "❌", "script-issue": "❌"}.get(issue_type, "❓")


def render_report(
    results: list[CheckResult],
    summary: Summary,
    workspace: Path,
) -> str:
    """Render full markdown report."""

    header = f"""# Python 脚本可运行性体检报告

- 体检时间: 2026-06-06
- 体检范围: {summary.total} 个 Python 脚本
- 体检深度: 静态检查 + 导入可行性 (未执行 main，未执行模块代码)
- 体检环境: master_study_env (只含 packaging/pip/setuptools/wheel)
- 工具脚本: tools/script_health_check.py
"""

    # Summary table
    clean_count = summary.total - summary.env_only_count - summary.script_issue_count
    summary_table = f"""## 汇总：环境 vs 脚本本身

| 维度 | 数量 |
|------|------|
| 脚本总数 | {summary.total} |
| 语法 OK | {summary.total - len(summary.syntax_failed)} |
| 语法失败 | {len(summary.syntax_failed)} |
| 脚本本身有问题 (语法/硬编码路径) | {summary.script_issue_count} |
| 只缺包、脚本本身健康 (env-only) | {summary.env_only_count} |
| 完全 clean | {clean_count} |

"""

    # Top missing modules
    mods_lines = "\n".join(
        f"- `{mod}` — {count} 个脚本依赖，env 内 MISSING → `pip install {mod}`"
        for mod, count in summary.import_missing_top
    ) if summary.import_missing_top else "- (无缺失模块)"
    missing_section = f"""## 缺失最多的模块 (Top {TOP_N})

{mods_lines}

"""

    # Priority recommendations
    priority = """## 优先级建议（基于修复工作量）

1. **易修复（仅装包）**: 装上缺失的包就能跑，列在 "env-only" 分组
2. **中等（装包 + 改路径）**: 还要把 F:/... 改成 __file__ 相对路径
3. **难（脚本本身有语法/逻辑问题）**: 需要人工 review

"""

    # Per-subproject detail
    detail_parts = ["## 按子项目分节详述（每个脚本一节）"]
    for sp_label, sp_results in summary.by_subproject.items():
        detail_parts.append(f"### {sp_label}/")
        for r in sorted(sp_results, key=lambda x: x.path):
            icon = _icon(r.issue_type)
            detail_parts.append(f"""#### {icon} {Path(r.path).name}  (issue_type: {r.issue_type})
- 语法: {'OK' if r.syntax_ok else r.syntax_error}
- 硬编码路径: {'无' if not r.hardcoded_paths else ', '.join(r.hardcoded_paths)}
- 全注释: {'是' if r.comments_only else '否'}
- Imports: {', '.join(r.imports) if r.imports else '(空)'}
- 缺失: {', '.join(f'{m} ({s})' for m, s in r.import_test.items() if s != 'OK') or '(无)'}
- 跳过 main: {'是' if r.skipped_main else '否'}
- 建议: {_recommendation(r)}
""")

    detail_section = "\n".join(detail_parts)

    return "\n".join([header, summary_table, missing_section, priority, detail_section])


def _recommendation(r: CheckResult) -> str:
    """Generate a short fix suggestion for a CheckResult."""
    if r.comments_only:
        return "该文件是文档伪装的 .py。如不需要可删除；如需保留请改成 `.md` 或启用代码"
    if not r.syntax_ok:
        return "打开文件修正语法错误"
    parts: list[str] = []
    missing_mods = [m for m, s in r.import_test.items() if s != "OK"]
    if missing_mods:
        parts.append(f"`pip install {' '.join(missing_mods)}`")
    if r.hardcoded_paths:
        parts.append("把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径")
    return "；".join(parts) if parts else "无需修改"


def render_chat_summary(
    results: list[CheckResult],
    summary: Summary,
) -> str:
    """Render a brief 3-5 line chat summary."""
    missing_top_3 = summary.import_missing_top[:3]
    top_mods_str = ", ".join(f"{m} ({c})" for m, c in missing_top_3) if missing_top_3 else "(无)"
    clean_count = summary.total - summary.env_only_count - summary.script_issue_count
    return (
        f"体检完成：{summary.total} 个 .py 脚本。"
        f"语法失败 {len(summary.syntax_failed)}，"
        f"硬编码路径 {len(summary.hardcoded_paths_files)} 个文件。\n"
        f"分类：env-only {summary.env_only_count}，"
        f"script-issue {summary.script_issue_count}，"
        f"clean {clean_count}。\n"
        f"最缺模块：{top_mods_str}。\n"
        f"详情见 docs/superpowers/reports/2026-06-06-python-script-health-check.md。"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    ws = Path(args.workspace).resolve()
    tool_path = Path(__file__).resolve()
    files = [f for f in discover_py_files(ws) if f.resolve() != tool_path]

    results: list[CheckResult] = []
    for f in files:
        results.append(check_file(f))

    summary = summarize(results)

    # Print summary to console
    print(f"Found {len(files)} .py files under {ws}")
    print(f"  Syntax failed:    {len(summary.syntax_failed)}")
    print(f"  Hardcoded paths:  {len(summary.hardcoded_paths_files)}")
    print(f"  Env-only issues:  {summary.env_only_count}")
    print(f"  Script issues:    {summary.script_issue_count}")
    print(f"  Top missing mods: {summary.import_missing_top[:5]}")
    print()

    # Write report
    report_dir = Path("docs/superpowers/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "2026-06-06-python-script-health-check.md"
    report_md = render_report(results, summary, ws)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"Report written to {report_path}")

    # Print chat summary
    print()
    print(render_chat_summary(results, summary))


if __name__ == "__main__":
    main()
