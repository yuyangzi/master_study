# Python 脚本可运行性体检 — 设计文档

- 日期: 2026-06-06
- 范围: 整个 master_study 工作区（51 个 .py）
- 目标: 在不动源码、不装深度学习包的前提下，给出每个脚本的"可运行性体检报告"

## 背景 & 约束

工作区 `master_study_env/` 是空的 conda 环境（只含 `packaging/pip/setuptools/wheel`），多数 ML 脚本依赖的 `torch/pandas/sklearn/numpy/matplotlib` 全部缺失。`graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/` 下大量脚本硬编码 `F:/...` Windows 路径，在 macOS 上必然失败。`sleep_classify/code/` 下脚本用相对路径，理论可跑但训练慢（100 epoch、165 个 xlsx）。

经过澄清，用户的诉求收敛在**可运行性体检**：

1. 任务目标：可运行性体检（不修路径、不装包）
2. 执行深度：静态检查 + 导入试验（不执行 `if __name__ == "__main__":`）
3. 环境策略：严格使用 `master_study_env` 原生状态
4. 报告格式：Markdown 文件 + 聊天总结

## 架构

单一驱动脚本 `tools/script_health_check.py`，~150 行，零外部依赖（仅 stdlib）。整体流程：

```
文件发现 (os.walk) → 逐文件体检 (5 步) → 汇总统计 → 报告渲染 (markdown)
```

`master_study_env/bin/python tools/script_health_check.py` 一行调用。

## 5 步体检（per file）

### Step 1: 语法检查
- 做法: `ast.parse(open(p, encoding='utf-8').read())`
- 失败: `SyntaxError` → `syntax_ok=False`，Step 2-4 全部跳过
- 字段: `syntax_ok: bool`, `syntax_error: str | None`

### Step 2: 提取 imports
- 做法: AST 遍历 `ast.Import` / `ast.ImportFrom`，收集所有顶层模块名 (e.g. `import torch.nn as x` → `torch`)，去重
- 不报错；空文件返回 `[]`

### Step 3: 硬编码路径扫描
- 做法: 正则 `r'[A-Z]:[\\/](?!\\?[/"])'` 匹配 `C:\...` `F:/...` `D:\foo` 等 Windows 路径，遍历所有 `ast.Str` / `ast.Constant` 字符串节点
- 失败: 列出前 5 条样本；不阻断

### Step 4: 试导入
- 做法: 对每个 unique 顶层 import 名调 `importlib.import_module(name)`，捕获 `ImportError / ModuleNotFoundError`
- 跳过相对导入（`.foo`），因无 `__package__` 上下文、误报率高
- 副作用隔离: 用临时 `HOME` 目录避免 import 时副作用污染用户 HOME（`matplotlib`/`torch` 等会写 `~/.matplotlib`、`~/.cache/torch`）
- 字段: `import_test: dict[str, str]`，形如 `{"torch": "OK"}` 或 `{"torch": "MISSING: ModuleNotFoundError: No module named 'torch'"}`

### Step 5: 跳过 main 执行
- 解析脚本时若 AST 含 `if __name__ == "__main__":` 节点，记录 `skipped_main=True`，**不执行**

## 数据结构

```python
@dataclass
class CheckResult:
    path: str                       # 相对 workspace 根
    syntax_ok: bool
    syntax_error: str | None
    imports: list[str]
    hardcoded_paths: list[str]
    import_test: dict[str, str]     # {module_name: "OK" | "MISSING: <reason>"}
    skipped_main: bool

@dataclass
class Summary:
    total: int
    syntax_failed: list[str]        # 路径列表
    import_missing_top: list[tuple[str, int]]  # 全局缺失 Top N
    hardcoded_paths_files: list[str]
    by_subproject: dict[str, dict]  # 子项目分组
```

## 子项目分组

| 子项目 | 路径特征 |
|--------|---------|
| `sleep_classify` | `graduation_transfer/sleep_posture/sleep_classify/` |
| `sleep_stage/IMU_sleep_stage-...` | 路径含 `IMU_sleep_stage-` |
| `sleep_stage/sleep_stage-迁移标签代码/` | 路径含 `sleep_stage-迁移标签代码/` |
| `sleep_stage/Sleep-pdf处理代码/` | 路径含 `Sleep-pdf处理代码/` |
| `__init__` | 文件名是 `__init__.py` |
| `other` | 兜底 |

## 错误处理

| 失败情形 | 处理 |
|---------|------|
| 文件读失败 (权限/编码) | 记录 `read_error`，标记 `syntax_ok=False`（无法检查），继续 |
| AST `SyntaxError` | 记录到 `syntax_error`，Step 2-4 全跳过，仍计入汇总 |
| `importlib` 抛 `ImportError` | 记录 `MISSING: <module>`，继续 |
| `importlib` 抛其他异常 (e.g. `OSError`, `ValueError`) | 记录 traceback 前 3 行，继续 |
| import 副作用污染 | 用临时 `HOME` 隔离；结束后还原 |
| 路径含中文/空格/括号 | `pathlib.Path` + `.relative_to(workspace_root)` 统一处理；报告中显示相对路径 |

## 报告结构

输出: `docs/superpowers/reports/2026-06-06-python-script-health-check.md`

```markdown
# Python 脚本可运行性体检报告

- 体检时间: ...
- 体检范围: N 个 Python 脚本
- 体检深度: 静态检查 + import 试验 (未执行 main)
- 体检环境: master_study_env (只含 packaging/pip/setuptools/wheel)
- 工具脚本: tools/script_health_check.py

## 汇总

| 子项目 | 脚本数 | 语法 OK | 含硬编码路径 | 导入全部成功 | 导入有缺失 |
|--------|--------|---------|-------------|-------------|-----------|

## 缺失最多的模块 (Top 10)
- `torch` — 35 个脚本依赖，env 内 MISSING
- ...

## 按子项目分节详述
### sleep_classify/code/
#### ✅ bp_algorithm.py
- 语法: OK
- 硬编码路径: 无
- Imports (4): ...
- 备注: ...
```

聊天总结包含：体检范围、子项目汇总表、3-5 条最优先解决的问题。

## 验收

| 验收点 | 通过条件 |
|--------|---------|
| 工具脚本自身不崩 | 用最小 `def foo(): pass` 测试文件试跑，输出 1 条结果 |
| 51 个脚本都被发现 | 报告 `total == 51` |
| SyntaxError 路径覆盖 | 临时 `bad_syntax.py` 用完即删，能正确标 `syntax_ok=False` |
| 硬编码路径检测覆盖 | 临时 `F:/foo/bar` 文件用完即删，能出现在 `hardcoded_paths` |
| ImportError 覆盖 | 现有 `bp_algorithm.py` 触发 torch MISSING |
| 报告可读 | 手动打开 md；中文路径不乱码 |
| 无副作用污染 | 跑完 `git status` 检查 `tools/` 和 `docs/` 之外无新文件 |

## 不做（YAGNI）

- 不写 `requirements.txt` / 不装任何包
- 不修复 `F:/` 路径
- 不执行 `if __name__ == "__main__":`
- 不跑训练 / 不读 `after_process_data/*.xlsx`
- 不 `git commit` 报告和工具脚本
- 不引入 pytest / 不写单元测试

## 产出物

- `tools/script_health_check.py` — 工具脚本
- `docs/superpowers/reports/2026-06-06-python-script-health-check.md` — 体检报告

## 下一步

调用 `writing-plans` skill 把本设计转为逐步实施计划。
