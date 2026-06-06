# Python 脚本可运行性体检 — 实施计划

- **Spec**: `docs/superpowers/specs/2026-06-06-python-script-health-check-design.md`
- **输出**: `tools/script_health_check.py` + `docs/superpowers/reports/2026-06-06-python-script-health-check.md`
- **状态**: ⏳ 待执行

## 依赖 DAG

```
Step 1 （脚手架）
  └── Step 2 （文件发现）
        └── Step 3 （体检 5 步，内部串行）
              └── Step 4 （分类 + 汇总）
                    └── Step 5 （报告渲染）
                          └── Step 6 （执行 + 验收）
                                └── Step 7 （commit）
```

每步必须在前一步验证通过后才开始。全部 7 步在一个文件 `tools/script_health_check.py` 里增量构建。

## 步骤

### Step 1 — 脚手架 + 数据结构

**Write** → `tools/script_health_check.py`:

```python
#!/usr/bin/env python3
"""Python script health check: syntax, imports, hardcoded paths, import feasibility."""

import ast
import argparse
import importlib.util
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
```

**数据结构**（对齐 spec §数据结构）：

```python
@dataclass
class CheckResult:
    path: str
    syntax_ok: bool = True
    syntax_error: Optional[str] = None
    imports: list[str] = field(default_factory=list)
    hardcoded_paths: list[str] = field(default_factory=list)
    comments_only: bool = False
    import_test: dict[str, str] = field(default_factory=dict)
    skipped_main: bool = False
    issue_type: str = ""

@dataclass
class Summary:
    total: int = 0
    syntax_failed: list[str] = field(default_factory=list)
    import_missing_top: list[tuple[str, int]] = field(default_factory=list)
    hardcoded_paths_files: list[str] = field(default_factory=list)
    by_subproject: dict[str, list[CheckResult]] = field(default_factory=dict)
    env_only_count: int = 0
    script_issue_count: int = 0
```

**CLI**:
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Python 脚本可运行性体检")
    parser.add_argument("workspace", nargs="?", default=".",
                        help="工作区根目录（默认当前目录）")
    return parser.parse_args()
```

**常量**:
- `WINDOWS_PATH_RE = re.compile(r'[A-Za-z]:[\\/](?!\\?)')`
- `SUBPROJECT_RULES` — list of (pattern, label)，按 spec §子项目分组 顺序
- `MAX_SAMPLES = 5`, `TOP_N = 10`

**空 `main()`**: 仅 `pass`。

**验证**:
```bash
master_study_env/bin/python tools/script_health_check.py --help
# → usage 帮助, exit 0

master_study_env/bin/python -c \
  "from tools.script_health_check import CheckResult, Summary; print('OK')"
# → OK, not ImportError
```

---

### Step 2 — 文件发现

**函数**: `discover_py_files(workspace: Path) -> list[Path]`

跳过目录: `master_study_env`, `.idea`, `__pycache__`, `.git`, `.opencode`, `node_modules`, 以及所有 `.` 开头的目录。

用 `os.walk` + 原地修改 `dirs[:]` 阻止进入被跳过目录。

返回按名字排序的绝对路径列表。

**验证**: 调用后确认 `len(files) == 51`。

---

### Step 3 — 体检 5 步

**函数**: `check_file(path: Path) -> CheckResult`

#### 3.1 语法检查
```python
try:
    source = open(path, encoding="utf-8", errors="replace").read()
    tree = ast.parse(source)
    syntax_ok, syntax_error, _tree = True, None, tree
except SyntaxError as e:
    syntax_ok, syntax_error, _tree = False, f"{e.msg} (line {e.lineno})", None
```
→ 后续步骤全部在 `if _tree is not None:` 内执行。

#### 3.2 提取 imports
```python
imports: set[str] = set()
for node in ast.walk(_tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            top = alias.name.split(".")[0]
            if not top.startswith("."):
                imports.add(top)
    elif isinstance(node, ast.ImportFrom):
        if node.module and not node.module.startswith("."):
            top = node.module.split(".")[0]
            imports.add(top)
```
→ result.imports = sorted(imports)

#### 3.3 硬编码路径扫描（AST 字符串）
```python
paths: list[str] = []
for node in ast.walk(_tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if WINDOWS_PATH_RE.search(node.value):
            paths.append(node.value.strip()[:120])
            if len(paths) >= MAX_SAMPLES:
                break
```
→ result.hardcoded_paths = paths

#### 3.4 Step 3b: 注释兜底
仅在 `imports` 为空 **且** `paths` 为空时触发。扫原始文件文本：
```python
comments_only = False
if not imports and not paths:
    raw = open(path, encoding="utf-8", errors="replace").read()
    matches = list(WINDOWS_PATH_RE.finditer(raw))
    if matches:
        comments_only = True
        for m in matches[:MAX_SAMPLES]:
            start = max(0, m.start() - 10)
            end = min(len(raw), m.end() + 60)
            paths.append(raw[start:end].strip()[:120])
```
→ result.comments_only = comments_only；若触发了，result.hardcoded_paths 包含注释中的路径样本

#### 3.5 导入可行性
对 result.imports 每个模块调 `importlib.util.find_spec(mod)`：
- `spec is not None` → `"OK"`
- `spec is None` → `"MISSING"`
- 抛异常 → `f"ERROR: {e}"`

存入 `result.import_test[mod] = status`

#### 3.6 main 守卫检测
```python
skipped_main = False
for node in ast.walk(_tree):
    if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
        left = node.test.left
        if isinstance(left, ast.Name) and left.id == "__name__":
            for op in node.test.ops:
                if isinstance(op, (ast.Eq, ast.Is)):
                    skipped_main = True
                    break
            if skipped_main:
                break
```
→ result.skipped_main = skipped_main

---

### Step 4 — 分类 + 汇总

**`classify(r: CheckResult) -> str`**:
```python
if r.comments_only:            return "all-commented"
if not r.syntax_ok:            return "script-issue"
has_script = bool(r.hardcoded_paths)
has_env    = any(v != "OK" for v in r.import_test.values())
if has_env and has_script:     return "mixed"
if has_env:                    return "env-only"
if has_script:                 return "script-issue"
return "clean"
```

**`summarize(results: list[CheckResult]) -> Summary`**:
- `.total = len(results)`
- `.syntax_failed` = paths where `not r.syntax_ok`
- `.import_missing_top` = 全局 Counter 统计缺失模块，取 TOP_N
- `.hardcoded_paths_files` = paths where `r.hardcoded_paths`
- `.by_subproject` = grouped by `subproject_of(r.path)`
- `.env_only_count` = count `r.issue_type == "env-only"`
- `.script_issue_count` = count `r.issue_type in ("script-issue", "all-commented", "mixed")`

**`subproject_of(path: Path) -> str`**: 按 `SUBPROJECT_RULES` 列表顺序匹配，返回第一个命中的 label。

**SUBPROJECT_RULES 定义**:
```python
SUBPROJECT_RULES = [
    ("__init__.py",           "__init__"),
    ("sleep_classify",        "sleep_classify"),
    ("IMU_sleep_stage",       "sleep_stage/IMU_sleep_stage"),
    ("迁移标签代码",            "sleep_stage/迁移标签"),
    ("Sleep-pdf处理代码",      "sleep_stage/Sleep-pdf"),
]
```

---

### Step 5 — 报告渲染

**`render_report(results, summary, workspace) -> str`**:
- 纯 f-string 拼接 markdown，对齐 spec §报告结构
- 脚本级别的 issue_type 映射图标：`clean`/`env-only`→ ✅, `all-commented`→ ⚠️, `script-issue`/`mixed`→ ❌
- 缺失模块建议: `pip install torch pandas ...` 拼接

**`render_chat_summary(results, summary) -> str`**: 3-5 行文本 summary。

**验证**: 输出合法的 markdown 字符串，中文路径不乱码。

---

### Step 6 — 执行 + 验收

```bash
master_study_env/bin/python tools/script_health_check.py
```

验收 9 条（spec §验收表）逐条验证。

**临时测试文件**（在工作区外 `/tmp/`）:
```bash
echo 'def foo(): pass' > /tmp/_test_basic.py
echo 'import syntax error' > /tmp/_test_bad_syntax.py
echo 'x = "F:/foo/bar"' > /tmp/_test_path_ast.py
echo '# F:/foo/bar comment only' > /tmp/_test_path_comment.py

master_study_env/bin/python tools/script_health_check.py /tmp
# → 预期: 4 个文件都被发现，_test_bad_syntax 标 syntax_ok=False
```

---

### Step 7 — Commit

```bash
git add tools/script_health_check.py docs/superpowers/reports/2026-06-06-python-script-health-check.md
git commit -m "feat(tools): add Python script health check tool and report"
echo "git push origin main（手动 PAT）"
```

---

## 验收点速查（9 条 @ spec）

| # | 验收点 | 对应步骤 |
|---|--------|---------|
| 1 | 工具自身不崩（最小 .py 测试） | 6 |
| 2 | total == 51 | 2 → 6 |
| 3 | SyntaxError 覆盖 | 3.1 → 6 |
| 4 | 硬编码路径 AST 检测 | 3.3 → 6 |
| 5 | 硬编码路径注释检测（feature_deal.py） | 3.4 → 6 |
| 6 | ImportError 覆盖（torch MISSING） | 3.5 → 6 |
| 7 | 报告可读 + 中文不乱码 + issue_type 分类 | 5 → 6 |
| 8 | 无副作用污染（git status 仅 tools/ 和 docs/） | 6 |
| 9 | 可重跑（CLI 参数） | 1 → 6 |

---

## 风险 & 缓解

| 风险 | 缓解 |
|------|------|
| `find_spec` 对 namespace package 返回非 None 但实际不可用 | 接受；spec 已说明这是"可发现性"而非"可运行性" |
| 51 文件 AST 解析 + 13 个模块 find_spec 耗时 | 预计 < 5 秒，无须并发 |
| 中文路径在 report 渲染时编码错 | `pathlib` + 文件 `encoding='utf-8'` 写入 |
| `feature_deal.py` 136 行注释扫原始文本可能慢 | 该文件仅 ~5KB，性能无关 |
| 子项目分组遗漏 Sleep-pdf（含 `-pdf` 和中文） | 用原字符串完全匹配，见 `SUBPROJECT_RULES` |

## 回滚

- **代码 bug**: 修复该步后重新运行，不影响已验证的步骤
- **结构性问题**: `git checkout -- tools/script_health_check.py` 重置
- **验收失败**: 修复后重跑 Step 6，已通过的验收点不再测

## 后续（本次不涉及）

- Git worktree 隔离（`using-git-worktrees`）
- 并行扫描（`dispatching-parallel-agents`）
- CI 集成 / JSON 输出 / Web 仪表板
