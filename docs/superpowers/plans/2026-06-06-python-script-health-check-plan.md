# Python 脚本可运行性体检 — 实施计划

- 日期: 2026-06-06
- 对应 spec: `docs/superpowers/specs/2026-06-06-python-script-health-check-design.md`
- 状态: ⏳ 待执行

## 总览

把 `tools/script_health_check.py`（~200 行 stdlib-only Python）建好，跑一次，输出报告到 `docs/superpowers/reports/2026-06-06-python-script-health-check.md`，然后 commit。

**一次性通过标准**：所有验收点 9 条全部 ✓。

## 步骤分解

### Phase A — 脚手架 & 数据结构（1 个 commit）

| # | 文件 | 改动 | 验证 |
|---|------|------|------|
| A1 | `tools/script_health_check.py` | 创建文件，写 `#!/usr/bin/env python3` 头、imports（`ast`, `argparse`, `importlib.util`, `os`, `pathlib`, `re`, `dataclasses`, `collections.Counter`）、CLI argparse（`WORKSPACE_DIR` 参数，默认 `.`）、`@dataclass CheckResult` 和 `Summary`、空 `main()` | `master_study_env/bin/python tools/script_health_check.py --help` 输出帮助 |
| A2 | （同 A1） | 加常量：`WINDOWS_PATH_RE = re.compile(r'[A-Z]:[\\/](?!\\?[/"])')`、`SUBPROJECT_RULES` 列表（按 spec 顺序）、`MAX_SAMPLES = 5` | 导入模块不报错 |

### Phase B — 文件发现 & 体检 5 步（1 个 commit）

| # | 改动 | 验证 |
|---|------|------|
| B1 | 实现 `discover_py_files(workspace: Path) -> list[Path]`，用 `os.walk` 遍历，跳过 `master_study_env/`、`.idea/`、`__pycache__/`、`*.pyc` | 加 debug print 显示发现 51 个 .py |
| B2 | 实现 `check_file(path: Path) -> CheckResult`，调用 5 步 | 单元式自检：跑最小脚本，输出 1 条结果 |
| B3 | Step 1: `ast.parse(open(p, encoding='utf-8').read())`，try/except SyntaxError + UnicodeDecodeError | bad_syntax.py 临时测试 |
| B4 | Step 2: AST 遍历 `ast.Import` / `ast.ImportFrom`，收集顶层 module 名（`import torch.nn as x` → `torch`），跳过 `from .relative import` | 简单脚本验证 |
| B5 | Step 3: 用 `WINDOWS_PATH_RE` 扫所有 `ast.Constant` 节点的 `value`（仅 `isinstance(value, str)`），列前 5 样本 | 临时 F:/ 文件测试 |
| B6 | Step 3b: 仅当 `imports == []` 且 Step 3 没找到路径时触发，扫原始文件 `open(p, encoding='utf-8', errors='replace').read()` 找路径，标 `comments_only=True` | feature_deal.py 应触发 |
| B7 | Step 4: 对每个 unique import 名 `importlib.util.find_spec(name)`，None → MISSING，ModuleSpec → OK，异常 → 记 traceback 前 3 行 | bp_algorithm.py 应标 torch MISSING |
| B8 | Step 5: 检查 AST 是否含 `if __name__ == "__main__":` 节点（任意位置），设 `skipped_main=True` | 19/51 脚本应正确标记 |

### Phase C — 分类 & 报告渲染（1 个 commit）

| # | 改动 | 验证 |
|---|------|------|
| C1 | 实现 `classify(result: CheckResult) -> str` 返回 `env-only` / `script-issue` / `mixed` / `clean` / `all-commented` | 单元验证 |
| C2 | 实现 `summarize(results: list[CheckResult]) -> Summary`（total、syntax_failed、import_missing_top 取前 10、hardcoded_paths_files、by_subproject、env_only_count、script_issue_count） | 输出合理 |
| C3 | 实现 `subproject_of(path: Path) -> str` 按 spec 顺序匹配（__init__ 先） | sleep_classify/code/ 应归 sleep_classify |
| C4 | 实现 `render_report(results, summary, workspace) -> str` 拼接 markdown 字符串（按 spec 的"报告结构"模板） | 中文路径不乱码 |
| C5 | 实现 `render_chat_summary(results, summary) -> str` 短摘要（3-5 条优先问题） | 简洁 |
| C6 | 在 `main()` 里串联：discover → check_file ×N → classify + summarize → render_report → 写到 `docs/superpowers/reports/2026-06-06-python-script-health-check.md` → print chat summary | 端到端跑通 |

### Phase D — 执行 & 验证（1 个 commit）

| # | 改动 | 验证 |
|---|------|------|
| D1 | 运行：`master_study_env/bin/python tools/script_health_check.py` | 不崩；退出码 0 |
| D2 | 检查 `git status` | 新文件仅在 `tools/` 和 `docs/superpowers/reports/` |
| D3 | 验证报告 `total == 51` | grep 数字 |
| D4 | 验证 `feature_deal.py` 被标 `all-commented` | grep |
| D5 | 验证 17 个文件含硬编码路径 | grep 计数 |
| D6 | 验证 `bp_algorithm.py` 含 torch MISSING | grep |
| D7 | 验证 19 个脚本 `skipped_main=True` | grep |
| D8 | 打开报告人工抽看 3 个脚本节 | 中文 OK，分类合理 |

### Phase E — 提交（1 个 commit）

| # | 改动 |
|---|------|
| E1 | `git add tools/ docs/superpowers/reports/` |
| E2 | `git commit -m "feat(tools): add Python script health check tool and report"` |
| E3 | `git push origin main`（你那边手动 PAT push） |

## 风险 & 缓解

| 风险 | 缓解 |
|------|------|
| `find_spec` 对某些 namespace package 返回非 None 但实际不可用 | 接受；spec 已说明这是"可发现性"而非"可运行性" |
| 51 文件 AST 解析 + 13 个唯一模块 find_spec 共耗时 | 实测预计 < 5 秒，无须并发 |
| 中文路径在 report 渲染时编码错 | 用 `pathlib` + `encoding='utf-8'`，并在写入时 `open(..., encoding='utf-8')` |
| `feature_deal.py` 136 行注释扫原始文本可能慢 | 该文件只有一个，最多 5KB；性能不是问题 |
| 子项目分组规则遗漏 `Sleep-pdf`（拼写 `Sleep-pdf处理代码`）| spec 用的就是这个字符串（含 `-pdf`），保持一致 |

## 验收（9 条 spec 已列）

实现完毕后对照 spec 验收表 9 条逐条 ✓。

## 后续（不在本次范围）

- 把工具接到 CI（如果需要）
- 加 `--json` 输出格式（如果需要）
- 改成 Web 仪表板（如果需要）
