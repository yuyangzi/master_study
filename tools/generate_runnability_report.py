#!/usr/bin/env python3
"""
生成 48 个 .py 脚本的可运行性报告（49 个真实脚本 - 1 跳过）。
读两份 run_results JSON + 静态扫描 .py 文件，输出 Markdown。

用法: venv/bin/python tools/generate_runnability_report.py [WORKSPACE]
"""
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

WORKSPACE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

# ── 数据结构 ──────────────────────────────────────────
@dataclass
class ScriptInfo:
    label: str
    rel_path: str
    group: str
    purpose: str
    imports: list[str] = field(default_factory=list)
    has_main: bool = False
    run_status: str = "not-run"   # success / failed / timeout / skipped / not-run
    exit_code: Optional[int] = None
    duration_s: float = 0.0
    error_type: Optional[str] = None
    error_summary: Optional[str] = None
    error_line: Optional[int] = None
    fix_hint: str = ""
    priority: str = ""            # P0-快 / P1-中 / P2-数据 / P3-GPU / P4-可忽略
    data_source: str = ""         # "" (未跑) / "old" (17:12 JSON) / "new" (本次)


# ── 子项目分组（按相对路径前缀） ──────────────────────────
GROUP_PATTERNS = [
    ("sleep_classify", "graduation_transfer/sleep_posture/sleep_classify/"),
    ("IMU",             "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage"),
    ("迁移",            "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/"),
    ("Sleep-pdf/data",  "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-"),
    ("Sleep-pdf/model", "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-"),
    ("Sleep-pdf/origin","graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/"),
]

def classify_group(rel: str) -> str:
    for label, pat in GROUP_PATTERNS:
        if pat in rel:
            return label
    return "other"

# ── 脚本发现 ──────────────────────────────────────────
def discover_scripts() -> list[Path]:
    grad = WORKSPACE / "graduation_transfer"
    out = []
    for py in grad.rglob("*.py"):
        if py.name == "__init__.py":
            continue
        if py.name == "feature_deal.py":  # 全注释伪 .py，跳过
            continue
        out.append(py)
    return sorted(out)


# ── "功能一句话"提取规则 ──────────────────────────────
def extract_purpose(path: Path) -> str:
    try:
        src = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"(无法读取: {e})"

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return f"(语法错误: {e.msg})"

    # 规则 1: module docstring
    doc = ast.get_docstring(tree)
    if doc:
        first = re.split(r"[。.!?!？\n]", doc.strip(), maxsplit=1)[0].strip()
        if first and len(first) >= 4:
            return first[:80]

    # 规则 2: if __name__ == "__main__": 块首字符串
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if (isinstance(test, ast.Compare) and
                isinstance(test.left, ast.Name) and test.left.id == "__name__" and
                len(test.comparators) == 1 and
                isinstance(test.comparators[0], ast.Constant) and
                test.comparators[0].value == "__main__"):
                for sub in node.body:
                    if isinstance(sub, ast.Expr) and isinstance(sub.value, ast.Constant):
                        if isinstance(sub.value.value, str) and len(sub.value.value) > 3:
                            return sub.value.value[:80]
                break

    # 规则 3: 文件名 + imports 启发式
    name = path.stem.lower()
    imports = extract_imports(tree)
    if "train" in name:
        return f"训练机器学习模型（{', '.join(imports[:3])}）"
    if "deal" in name or "preprocess" in name:
        return f"数据预处理脚本（{', '.join(imports[:3])}）"
    if "extract" in name:
        return f"数据提取脚本（{', '.join(imports[:3])}）"
    if "chart" in name or "figure" in name or "imag" in name:
        return "生成可视化图表/混淆矩阵"
    if "test" in name:
        return "测试/验证脚本"
    if "count" in name:
        return "统计/计数脚本"

    return "(无法推断)"

def extract_imports(tree: ast.AST) -> list[str]:
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
    return sorted(mods)

def has_main_block(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if (isinstance(test, ast.Compare) and
                isinstance(test.left, ast.Name) and test.left.id == "__name__" and
                len(test.comparators) == 1 and
                isinstance(test.comparators[0], ast.Constant) and
                test.comparators[0].value == "__main__"):
                return True
    return False


# ── 错误行号提取 ──────────────────────────────────────
_LINE_RE = re.compile(r'line (\d+), in <module>')

def extract_error_line(stderr: str) -> Optional[int]:
    m = _LINE_RE.search(stderr)
    return int(m.group(1)) if m else None

# ── 修复提示模板 ──────────────────────────────────────
def make_fix_hint(error_type: str, error_detail: str, error_line: Optional[int]) -> str:
    line_str = f"第 {error_line} 行" if error_line else "相应位置"
    et = (error_type or "").lower()
    if "nameerror" in et:
        m = re.search(r"name '(\w+)'", error_detail or "")
        var = m.group(1) if m else "X"
        return f"变量 `{var}` 未定义。原因：可能未初始化或被注释。修复：{line_str} 附近加 `{var} = ...`"
    if "prefetch_factor" in (error_detail or ""):
        return f"PyTorch 2.x 不允许 num_workers=0 时设 prefetch_factor。修复：{line_str} 的 `DataLoader(...)` 删除 `prefetch_factor=2` 参数"
    if "too many dimensions" in (error_detail or ""):
        return f"pandas Series 直接喂 torch.tensor 报错。修复：{line_str} `torch.tensor(y_train)` 改为 `torch.tensor(y_train.values)`"
    if "liblinear" in (error_detail or "") and "multiclass" in (error_detail or ""):
        return f"liblinear 不支持 3 分类。修复：{line_str} `solver='liblinear'` 改为 `solver='lbfgs'`"
    if "sheet is too large" in (error_detail or ""):
        return f"Excel 行数超过 1048576 上限。修复：{line_str} `df.to_excel(...)` 改为 `df.to_csv(...)` 或拆 sheet"
    if "filenotfounderror" in et:
        if "kd_tree.m" in (error_detail or ""):
            return "模型未训练。修复：先跑 kdtree_data.py 生成 ../model/kd_tree.m"
        if any(x in (error_detail or "") for x in [".txt", ".csv", ".hex", ".edf"]):
            return "IMU 原始数据缺失。修复：把被试数据放到 data/ 目录，或检查 Path(__file__) 推导是否正确"
        return "数据文件不存在。修复：检查路径或补充数据"
    if "modulenotfounderror" in et:
        m = re.search(r"No module named '(\S+)'", error_detail or "")
        mod = m.group(1) if m else "?"
        return f"缺包。修复：`pip install {mod}`"
    if "timeout" in et:
        return "训练耗时长。修复：加长 timeout（如 600s）或减少数据量/epochs"
    return "(手工诊断)"


# ── 优先级判定（先匹配先赢） ──────────────────────────
def classify_priority(info: ScriptInfo, path: Path) -> str:
    src = path.read_text(encoding="utf-8") if path.exists() else ""
    # P4: 全注释伪 .py
    if not info.imports and ("# " in src or "#" in src) and "def " not in src:
        return "⚪ P4-可忽略"
    # P4: 无 main 且无 I/O 副作用
    if not info.has_main and "open(" not in src and "to_csv" not in src and "to_excel" not in src:
        return "⚪ P4-可忽略"
    # P3: torch + 训练循环
    if "torch" in info.imports and ("range(" in src or "for epoch" in src.lower()):
        return "🔵 P3-GPU"
    # P2: FileNotFoundError
    if info.error_type and "filenotfounderror" in info.error_type.lower():
        return "🟠 P2-数据"
    # P0: 单行修复
    if info.error_type in ("NameError",) or any(k in (info.error_summary or "")
            for k in ["prefetch_factor", "liblinear", "sheet is too large", "too many dimensions"]):
        return "🟢 P0-快"
    # P1: 其余
    return "🟡 P1-中"


# ── 合并两份 JSON ──────────────────────────────────────
def load_results() -> list[dict]:
    """合并两份 run_results JSON；缺失/解析失败时返回空 list 不抛错。"""
    out = []
    old = WORKSPACE / "docs/superpowers/reports/run_results.json"          # 17:12 5 条 sleep_classify
    new = WORKSPACE / "docs/superpowers/reports/run_results-sleep_stage.json"  # 29 条（本次）
    for f, tag in [(old, "old"), (new, "new")]:
        if not f.exists():
            print(f"WARN: {f.name} not found, skipping", file=sys.stderr)
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"WARN: {f.name} parse error: {e}", file=sys.stderr)
            continue
        for r in data:
            r["data_source"] = tag
            out.append(r)
    return out

# ── 扫描所有 48 个脚本 ──────────────────────────────────
def scan_all_scripts() -> dict[str, ScriptInfo]:
    """key = rel_path（绝对唯一），避免 psg_rnn_lstm / test 这样的 stem 冲突覆盖。"""
    out = {}
    for path in discover_scripts():
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except Exception:
            tree = None
            src = ""
        rel = str(path.relative_to(WORKSPACE))
        info = ScriptInfo(
            label=path.stem,
            rel_path=rel,
            group=classify_group(rel),
            purpose=extract_purpose(path) if tree else "(语法错误)",
            imports=extract_imports(tree) if tree else [],
            has_main=has_main_block(tree) if tree else False,
        )
        out[rel] = info  # ← 用 rel_path 作 key（不是 path.stem）
    return out

# ── 把执行结果合并到 ScriptInfo ──────────────────────────
def merge_results(scripts: dict[str, ScriptInfo], results: list[dict]):
    """匹配顺序：rel_path 精确 > rel_path 末段 > label 字符串。
    覆盖了「旧 JSON 5 条 label 命名不一致」「psg_rnn_lstm 同名」「test 同名」三类场景。
    """
    # 1) 构建 rel_path 末段 -> info 的反向索引
    by_stem_suffix: dict[str, ScriptInfo] = {
        Path(k).name: v for k, v in scripts.items()
    }

    matched = 0
    for r in results:
        # JSON 里 script 字段是绝对路径，转 rel_path
        r_rel = str(Path(r["script"]).relative_to(WORKSPACE))
        info = None
        # 1) 精确匹配 rel_path
        if r_rel in scripts:
            info = scripts[r_rel]
        # 2) 末段文件名匹配（应对"只存了 stem 不是 rel_path"的老 JSON）
        elif Path(r_rel).name in by_stem_suffix:
            info = by_stem_suffix[Path(r_rel).name]
        # 3) 退化：按 label 字符串匹配
        elif r.get("label") in [i.label for i in scripts.values()]:
            info = next(i for i in scripts.values() if i.label == r["label"])
        if info is None:
            print(f"WARN: no script match for {r_rel} (label={r.get('label')})", file=sys.stderr)
            continue
        matched += 1
        info.run_status = "success" if r.get("exit_code") == 0 and not r.get("timeout") else \
                          "timeout" if r.get("timeout") else "failed"
        info.exit_code = r.get("exit_code")
        info.duration_s = r.get("duration_s", 0.0)
        info.error_type = r.get("error_type")
        info.error_summary = (r.get("error_detail") or "")[:200]
        info.error_line = extract_error_line(r.get("stderr", ""))
        # 成功脚本不需要修复提示（make_fix_hint(None,...) 会返回 "(手工诊断)"，会误导）
        info.fix_hint = (
            make_fix_hint(info.error_type, r.get("error_detail", ""), info.error_line)
            if info.run_status != "success" else ""
        )
        info.data_source = r.get("data_source", "old")
    print(f"merge_results: matched {matched}/{len(results)} run entries", file=sys.stderr)

    # 优先级判定
    for rel, info in scripts.items():
        full_path = WORKSPACE / info.rel_path
        info.priority = classify_priority(info, full_path)


# ── Markdown 渲染 ──────────────────────────────────────
def render_markdown(scripts: dict[str, ScriptInfo]) -> str:
    lines = []
    w = lines.append

    w("# 脚本可运行性报告")
    w("")
    w("- 运行时间: 2026-06-06")
    w("- 范围: graduation_transfer/ 48 个 .py 脚本（49 个真实脚本 - 1 跳过 = 48；额外 1 条 `data_deal/test.py` 在磁盘但不在 SCRIPTS_ALL）")
    w("- 数据源: 5 旧 (17:12 run_results.json) + 29 新 (本次) + 14 未跑 + 1 跳过（feature_deal.py）")
    w("- 环境: venv (Python 3.11, macOS ARM64, torch 2.12 CPU)")
    w("")

    # 汇总
    status_count = {"success": 0, "failed": 0, "timeout": 0, "skipped": 0, "not-run": 0}
    priority_count = {"🟢 P0-快": 0, "🟡 P1-中": 0, "🟠 P2-数据": 0, "🔵 P3-GPU": 0, "⚪ P4-可忽略": 0}
    for info in scripts.values():
        status_count[info.run_status] = status_count.get(info.run_status, 0) + 1
        priority_count[info.priority] = priority_count.get(info.priority, 0) + 1
    # 硬编码 1 跳过（feature_deal.py）— 它在 discover_scripts() 中被过滤掉，不会出现在 scripts 字典里
    status_count["skipped"] = 1

    w("## 汇总")
    w("")
    w("| 状态 | 数量 |")
    w("|---|---|")
    w(f"| ✅ 运行成功 | {status_count['success']} |")
    w(f"| ❌ 失败 | {status_count['failed']} |")
    w(f"| ⏱ 超时 | {status_count['timeout']} |")
    w(f"| ⚠️ 跳过 | {status_count['skipped']} |（feature_deal.py 全注释）")
    w("")

    w("## 修复优先级")
    w("")
    w("| 优先级 | 数量 | 处理建议 |")
    w("|---|---|---|")
    w(f"| 🟢 P0-快 | {priority_count['🟢 P0-快']} | 现在修，~5 分钟 |")
    w(f"| 🟡 P1-中 | {priority_count['🟡 P1-中']} | 今天修，~30 分钟 |")
    w(f"| 🟠 P2-数据 | {priority_count['🟠 P2-数据']} | 数据到位后修 |")
    w(f"| 🔵 P3-GPU | {priority_count['🔵 P3-GPU']} | 上服务器跑 |")
    w(f"| ⚪ P4-可忽略 | {priority_count['⚪ P4-可忽略']} | 视情况 |")
    w("")

    # 按 group 分节
    group_order = ["sleep_classify", "IMU", "迁移", "Sleep-pdf/data", "Sleep-pdf/model", "Sleep-pdf/origin"]
    for grp in group_order:
        members = [info for info in scripts.values() if info.group == grp]
        if not members:
            continue
        w(f"### {grp}（{len(members)} 条）")
        w("")
        for info in sorted(members, key=lambda x: x.label):
            render_script(w, info)
            w("")

    # 跳过的脚本
    w("### 跳过的脚本")
    w("")
    w("- `feature_deal.py` — 全注释伪 .py，136 行全部注释")
    w("")

    # 附录
    w("## 附录")
    w("")
    w("- 跑 29 个脚本: `tools/run_analysis.py --filter sleep_stage`")
    w("- 重新生成报告: `tools/generate_runnability_report.py`")
    w("- 旧 run_results.json: 17:12 5 条 sleep_classify 验证")
    w("- 旧 run-analysis-report.md: 15:29 18 个完整分析（markdown，无法结构化合并）")
    w("")
    return "\n".join(lines)

def render_script(w, info: ScriptInfo):
    icon = {"success": "✅", "failed": "❌", "timeout": "⏱", "skipped": "⚠️", "not-run": "❔"}.get(info.run_status, "❔")
    w(f"#### {icon} `{info.label}.py`")
    w("")
    w(f"- 路径: `{info.rel_path}`")
    w(f"- 功能: {info.purpose}")
    w(f"- Imports: {', '.join(info.imports[:5]) or '(空)'}")
    if info.run_status != "not-run":
        w(f"- 运行: exit={info.exit_code}, {info.duration_s:.1f}s")
    if info.error_type:
        w(f"- 错误: `{info.error_type}: {info.error_summary}`")
    if info.error_line:
        w(f"- 行号: {info.error_line}")
    if info.fix_hint:
        w(f"- 修复: {info.fix_hint}")
    if info.priority:
        w(f"- 优先级: {info.priority}")
    if info.data_source:
        w(f"- 数据源: {'新 (本次)' if info.data_source == 'new' else '旧 (17:12 JSON)'}")
    w("")


def main():
    scripts = scan_all_scripts()
    results = load_results()
    merge_results(scripts, results)

    md = render_markdown(scripts)
    out = WORKSPACE / "docs/superpowers/reports/2026-06-06-script-runnability-report.md"
    out.write_text(md, encoding="utf-8")
    print(f"Report written to {out}")
    print(f"Total scripts: {len(scripts)}")
    status_count = {"success": 0, "failed": 0, "timeout": 0, "skipped": 0, "not-run": 0}
    for info in scripts.values():
        status_count[info.run_status] = status_count.get(info.run_status, 0) + 1
    # 硬编码 1 跳过（feature_deal.py）— 它在 discover_scripts() 中被过滤掉，不会出现在 scripts 字典里
    status_count["skipped"] = 1
    for s, c in status_count.items():
        print(f"  {s}: {c}")

if __name__ == "__main__":
    main()
