# Python 脚本可运行性体检 — 设计文档

- 日期: 2026-06-06
- 范围: 整个 master_study 工作区（51 个 .py）
- 目标: 在不动源码、不装深度学习包的前提下，给出每个脚本的"可运行性体检报告"，并对每类失败提供**最小可执行的修复建议**

## 背景 & 约束

工作区 `master_study_env/` 是空的 conda 环境（只含 `packaging/pip/setuptools/wheel`），多数 ML 脚本依赖的 `torch/pandas/sklearn/numpy/matplotlib` 全部缺失。`graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/` 下大量脚本硬编码 `F:/...` Windows 路径，在 macOS 上必然失败。`sleep_classify/code/` 下脚本用相对路径，理论可跑但训练慢（100 epoch、165 个 xlsx）。

经过澄清（+ Metis 审查），用户的诉求收敛在**可运行性体检 + 最小修复建议**：

1. 任务目标：可运行性体检（不修路径、不装包）+ 每类失败给出可执行修复建议
2. 执行深度：静态检查 + 导入可行性（不执行 `if __name__ == "__main__":`）
3. 环境策略：严格使用 `master_study_env` 原生状态
4. 报告格式：Markdown 文件 + 聊天总结
5. 工具可重用：脚本独立可重跑，CLI 稳定

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

### Step 3: 硬编码路径扫描（AST 字符串）
- 做法: 正则 `r'[A-Z]:[\\/](?!\\?[/"])'` 匹配 `C:\...` `F:/...` `D:\foo` 等 Windows 路径，遍历所有 `ast.Str` / `ast.Constant` 字符串节点
- 失败: 列出前 5 条样本；不阻断
- 注释里的硬编码路径**不会**被此步捕获（注释不进 AST），由 Step 3b 兜底

### Step 3b: 硬编码路径扫描（注释 / 全注释文件兜底）
- 触发条件: 脚本 import 列表为空且 Step 3 没找到硬编码路径（即可能是 `feature_deal.py` 这种"全注释伪 .py"）
- 做法: 读原始文件文本，用同一正则扫所有出现位置
- 标记: 若发现匹配 → 标 `comments_only: True`（说明文件没有可执行代码）

### Step 4: 导入可行性（不执行模块代码）
- 做法: 对每个 unique 顶层 import 名调 `importlib.util.find_spec(name)`
  - 返回 `ModuleSpec` → 标记 `OK`（模块**可被发现**，不验证运行）
  - 返回 `None` → 标记 `MISSING`
  - 抛其他异常 → 记录 traceback 前 3 行
- **零执行**：不调用 `importlib.import_module`，避免触发目标模块的 `__init__.py` 代码 / 副作用
- 跳过相对导入（`.foo`），因无 `__package__` 上下文、误报率高
- 字段: `import_test: dict[str, str]`，形如 `{"torch": "OK"}` 或 `{"torch": "MISSING"}`

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
    hardcoded_paths: list[str]      # Step 3 找到的（AST 字符串）
    comments_only: bool             # Step 3b 触发：全注释伪 .py
    import_test: dict[str, str]     # {module_name: "OK" | "MISSING: <reason>"}
    skipped_main: bool
    issue_type: str                 # "env-only" | "script-issue" | "mixed" | "clean"

@dataclass
class Summary:
    total: int
    syntax_failed: list[str]        # 路径列表
    import_missing_top: list[tuple[str, int]]  # 全局缺失 Top N（最多 10）
    hardcoded_paths_files: list[str]
    by_subproject: dict[str, dict]  # 子项目分组
    env_only_count: int             # 只缺包、脚本本身健康的脚本数
    script_issue_count: int         # 有脚本本身问题（语法/路径）的脚本数
```

## 子项目分组（应用顺序：先匹配先赢）

1. `__init__` — 文件名是 `__init__.py`（先匹配，零字节也算）
2. `sleep_classify` — 路径含 `graduation_transfer/sleep_posture/sleep_classify/`
3. `sleep_stage/IMU_sleep_stage` — 路径含 `IMU_sleep_stage-`
4. `sleep_stage/迁移标签` — 路径含 `sleep_stage-迁移标签代码/`
5. `sleep_stage/Sleep-pdf` — 路径含 `Sleep-pdf处理代码/`
6. `other` — 兜底

## 错误处理

| 失败情形 | 处理 |
|---------|------|
| 文件读失败 (权限/编码) | 记录 `read_error`，标记 `syntax_ok=False`（无法检查），继续 |
| AST `SyntaxError` | 记录到 `syntax_error`，Step 2-3b 全跳过，仍计入汇总 |
| `find_spec` 返回 `None` | 记录 `MISSING`，继续 |
| `find_spec` 抛其他异常 (e.g. `OSError`, `ValueError`) | 记录 traceback 前 3 行，继续 |
| 路径含中文/空格/括号 | `pathlib.Path` + `.relative_to(workspace_root)` 统一处理；报告中显示相对路径 |
| （已删除）临时 HOME 隔离 | 不再需要，`find_spec` 零执行 |

## 报告结构

输出: `docs/superpowers/reports/2026-06-06-python-script-health-check.md`

```markdown
# Python 脚本可运行性体检报告

- 体检时间: 2026-06-06 HH:MM
- 体检范围: N 个 Python 脚本
- 体检深度: 静态检查 + 导入可行性 (未执行 main，未执行模块代码)
- 体检环境: master_study_env (只含 packaging/pip/setuptools/wheel)
- 工具脚本: tools/script_health_check.py

## 汇总：环境 vs 脚本本身

| 维度 | 数量 |
|------|------|
| 脚本总数 | 51 |
| 语法 OK | 48 |
| 脚本本身有问题 (语法/硬编码路径) | ? |
| 只缺包、脚本本身健康 (env-only) | ? |
| 混合型 (env + 脚本) | ? |
| 完全 clean | 0 (env 几乎全空) |

## 缺失最多的模块 (Top N，N ≤ 10)
- `torch` — 35 个脚本依赖，env 内 MISSING → `pip install torch`
- `pandas` — 28 个脚本依赖，env 内 MISSING → `pip install pandas`
- ...

## 优先级建议（基于修复工作量）

1. **🟢 易修复（仅装包）**: 装上缺失的包就能跑，列在 "env-only" 分组
2. **🟡 中等（装包 + 改路径）**: 还要把 `F:/...` 改成 `__file__` 相对路径
3. **🔴 难（脚本本身有语法/逻辑问题）**: 需要人工 review

## 按子项目分节详述（每个脚本一节）
### sleep_classify/code/
#### ✅ bp_algorithm.py  (issue_type: env-only)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: feature1, feature2, ..., torch, pandas, sklearn
- 缺失: torch (建议 `pip install torch`), pandas (建议 `pip install pandas`)
- 跳过 main: 是
- 建议: `pip install torch pandas scikit-learn`

#### ⚠️ feature_deal.py  (issue_type: all-commented)
- 语法: OK（解析成功，但无 active code）
- 硬编码路径: 注释中找到 E:/master_paper/...
- 全注释: **是** — 136 行全部被注释掉
- Imports: (空)
- 建议: 该文件是文档伪装的 .py。如不需要可删除；如需保留改成 `.md` 或启用代码

#### ❌ descison_tree.py  (issue_type: script-issue)
- 语法: SyntaxError: ...
- ...
- 建议: 打开文件看具体错误位置

#### ❌ eeg_data_deal_1.py  (issue_type: mixed)
- 语法: OK
- 硬编码路径: `F:/master_paper/...`, `F:/ysl/...`
- Imports: torch, mne, ...
- 缺失: torch, mne
- 建议: 1) `pip install torch mne`  2) 把 `F:/...` 改成 `pathlib.Path(__file__).parent / "..."`
```

聊天总结包含：体检范围、环境 vs 脚本汇总、3-5 条最优先解决的问题（从"优先级建议"提炼）。

## 验收

| 验收点 | 通过条件 |
|--------|---------|
| 工具脚本自身不崩 | 用最小 `def foo(): pass` 测试文件试跑，输出 1 条结果 |
| 51 个脚本都被发现 | 报告 `total == 51` |
| SyntaxError 路径覆盖 | 临时 `bad_syntax.py` 用完即删，能正确标 `syntax_ok=False` |
| 硬编码路径检测覆盖 (AST) | 临时 `F:/foo/bar` 文件用完即删，能出现在 `hardcoded_paths` |
| 硬编码路径检测覆盖 (注释) | `feature_deal.py` 的注释路径能被 Step 3b 捕获 |
| ImportError 覆盖 | 现有 `bp_algorithm.py` 触发 torch MISSING（用 `find_spec`） |
| 报告可读 | 手动打开 md；中文路径不乱码；含 "env-only / script-issue / mixed" 分类 |
| 无副作用污染 | 跑完 `git status`，新文件**仅**在 `tools/` 和 `docs/superpowers/reports/` 内出现 |
| 可重跑 | 工具支持 `python tools/script_health_check.py [WORKSPACE_DIR]` CLI 参数，默认 cwd |

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

## 决策记录（Metis 审查 → 默认决策）

| 议题 | Metis 担忧 | 采用决策 | 理由 |
|------|----------|---------|------|
| Step 4 用 import_module 还是 find_spec | import_module 触发 `__init__.py`，违反"不执行" | **`find_spec`** | 零执行，零副作用；也消除了"临时 HOME"的需要 |
| 是否加推荐解决方案 | 用户原话要过；空 env 下报告空洞 | **加最小可执行建议** | `pip install xxx` + 路径修复提示；每脚本的 issue_type 分类 |
| feature_deal.py 怎么标 | 全注释伪 .py 不进 AST 节点 | **加 Step 3b + `comments_only: True` 标记** | 扫原始文本兜底；显式标记让用户看到 |
| 工具一次 vs 可重用 | 一次性报告 schema 不稳定 | **可重用** + CLI 参数 | 脚本小，无额外成本；以后装包/改路径后还能重跑 |
| 临时 HOME 隔离 | 复杂、跨平台坑 | **删除** | `find_spec` 零执行，副作用不存在 |
| Top 10 缺失 | 实际只有 13 个唯一第三方 | **Top N (N ≤ 10)** | 实际全列；超过 10 才截断 |

## 下一步

调用 `writing-plans` skill 把本设计转为逐步实施计划。
