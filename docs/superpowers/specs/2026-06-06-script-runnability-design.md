# 脚本可运行性报告 — 设计文档

- 日期: 2026-06-06
- 范围: graduation_transfer/ 下的 48 个 .py 脚本（49 个真实脚本 - 1 跳过 = 48，+1 漏网 `data_deal/test.py` 在磁盘但不在 SCRIPTS_ALL，报告里以 "not-run" 出现）
- 目标: 跑 29 个新修过路径的 sleep_stage 脚本，结合 5 条 17:12 已有 JSON 结果（**不是 18 条 markdown 报告**），生成一份**全量可运行性报告**：每个脚本一句话功能描述、能否跑通、失败原因、修复提示（带行号）、按难度推荐修复优先级

## 背景 & 约束

仓库的 51 个 .py 文件分布如下（含 2 个 `__init__.py`，49 个真实脚本）：

| 位置 | 真实脚本数 | 状态 |
|------|------|------|
| `sleep_posture/sleep_classify/code/` | 10 | 10 个 15:29 报告，17:12 JSON 3 条 |
| `sleep_posture/sleep_classify/util/` | 1 | 1 个 15:29 报告，17:12 JSON 0 条 |
| `sleep_stage/.../IMU_sleep_stage.../data_deal_code/` | 4 | 0 已分析，4 待新跑 |
| `sleep_stage/.../IMU_sleep_stage.../model/` | 7 | 0 已分析，7 待新跑 |
| `sleep_stage/.../sleep_stage-迁移标签代码/code-.../` | 7 | 1 已分析（test_all），6 待新跑；17:12 JSON 1 条 |
| `sleep_stage/.../sleep_stage-迁移标签代码/model/` | 1 | 0 已分析，1 待新跑 |
| `sleep_stage/.../Sleep-pdf处理代码/new_project/data_deal-.../` | 6 | 2 已分析（test_psg_data + test.py 漏网），3 待新跑（feature_deal.py 跳过） |
| `sleep_stage/.../Sleep-pdf处理代码/new_project/model-.../` | 11 | 3 已分析，8 待新跑 |
| `sleep_stage/.../Sleep-pdf处理代码/new_project/origin_data_deal/` | 2 | 1 已分析，1 已分析（origin_test=15:29 报告 / test.py） |
| `**/__init__.py` | 2 | 跳过（init 模板） |

合计 51 文件 / 49 真实脚本 = 5 旧（17:12 JSON 实有）+ 29 新（SCRIPTS_ALL[18:]）+ 1 漏网（`data_deal/test.py`）+ 14 未跑（旧 sleep_classify 中 13 个未在 17:12 JSON 留下数据的）+ 1 跳过（feature_deal.py 全注释）。

> **⚠️ 旧报告数据 vs 旧 JSON 数据**：
> - 15:29 markdown 报告（`run-analysis-report.md`）有 18 个 sleep_classify 条目的分析
> - 17:12 JSON（`run_results.json`）只有 5 条实际跑过的 sleep_classify 数据
> - 本次 `merge_results()` 只能拿到 5 条 JSON 数据，**13 个旧 sleep_classify 脚本会以 "not-run" 出现**（它们的旧分析信息无法结构化合并）

经过 7 轮澄清，用户的诉求收敛：

1. **数据来源**：只跑 29 个新修过路径的 sleep_stage 脚本（~15 分钟），不再重跑 sleep_classify
2. **报告范围**：48 个 .py 脚本（49 真实 - 1 跳过 = 48，+1 漏网以 not-run 出现）
3. **修复建议详度**：描述 + 修复提示 + 具体行号（不贴完整 diff）
4. **报告输出路径**：`docs/superpowers/reports/2026-06-06-script-runnability-report.md`
5. **执行配置**：120s timeout + 详细 stdout/stderr 捕获（与之前 run_analysis 一致）
6. **报告定位**：诊断 + 按难度/价值推荐修复优先级（不是纯诊断，也不包含详细工时估算）
7. **实现方案**：扩展 `tools/run_analysis.py`（不另起炉灶）

## 架构

两层：

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: 执行（tools/run_analysis.py 扩展）                  │
│  --filter sleep_stage：发现 sleep_stage/ 下 29 个 .py       │
│  复用 subprocess.run + 120s timeout 逻辑                     │
│  写 run_results-sleep_stage.json（不覆盖旧 run_results）     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: 报告生成（tools/generate_runnability_report.py 新建）│
│  读 run_results-sleep_stage.json + 旧 run_results.json +    │
│      静态扫描 48 个 .py 文件（AST 提功能/行号）               │
│  错误分类 → 修复提示 → Markdown 渲染                        │
│  输出 2026-06-06-script-runnability-report.md               │
└─────────────────────────────────────────────────────────────┘
```

不修改 `run_results.json`（保留 17:12 的 5 条 sleep_classify 部分结果作为审计线索）。新结果单独存。

## Component 1: `tools/run_analysis.py` 扩展

### 新增 CLI 参数
```python
parser.add_argument("--filter", choices=["all", "sleep_classify", "sleep_stage"],
                    default="all", help="脚本发现过滤器")
parser.add_argument("--output", default=None,
                    help="JSON 输出文件路径，默认 docs/superpowers/reports/run_results.json")
parser.add_argument("--dry-run", action="store_true",
                    help="仅打印发现列表 + OUTPUT 路径，不实际执行")
parser.add_argument("--print-output", action="store_true",
                    help="仅打印 OUTPUT 路径")
```

### 脚本发现逻辑（按 filter）
- `all`：保留现有逻辑（29 sleep_stage + 18 sleep_classify + 1 漏网 = 48 条）
- `sleep_classify`：只发现 `graduation_transfer/sleep_posture/sleep_classify/` 下 .py
- `sleep_stage`：只发现 `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/` 下 .py，**排除** `__init__.py`

### 输出文件名
- 不带 `--output` 时，按 filter 自动命名：
  - `all` → `run_results.json`
  - `sleep_classify` → `run_results-sleep_classify.json`
  - `sleep_stage` → `run_results-sleep_stage.json`
- 带 `--output` 时用指定值（覆盖自动命名）

### 改动原则
- 改最小集：只加 4 个参数 + 1 个发现分支 + 1 个输出文件命名逻辑
- 原有 18 个 sleep_classify 脚本的 `label/script/workdir` 不变（向后兼容）
- 不动 `docs/superpowers/reports/2026-06-06-run-analysis-report.md`（旧报告保留）

## Component 2: `tools/generate_runnability_report.py` 新建

~280 行，零外部依赖（仅 stdlib）。整体流程：

```
读旧 run_results.json（17:12，5 条）
    ↓
读新 run_results-sleep_stage.json（29 条，Layer 1 跑完才有）
    ↓
静态扫描 48 个 .py 文件
  - ast.parse 语法
  - 提 module docstring（功能一句话）
  - 提 __name__ == "__main__" 块的 docstring / 第一个 print
  - 提文件顶层 import 模块名（用于缺包提示）
  - 对失败文件：用 traceback 反查文件行号（从 error_detail 提 lineno）
    ↓
合并两层数据：按脚本 rel_path 归一（rel_path 是绝对唯一的，避免 psg_rnn_lstm/test 同名覆盖）
    ↓
分类、排序、生成 Markdown
    ↓
写 2026-06-06-script-runnability-report.md
```

### 静态扫描数据结构
```python
@dataclass
class ScriptInfo:
    label: str                   # 报告中的简短名（去扩展名）
    rel_path: str                # 相对 workspace 根
    group: str                   # sleep_classify / IMU / 迁移 / Sleep-pdf
    purpose: str                 # 一句话功能（提取规则见下）
    imports: list[str]           # 顶层 import 模块名
    has_main: bool               # 是否含 if __name__ == "__main__":
    run_status: str              # "success" | "failed" | "timeout" | "skipped" | "not-run"
    exit_code: int | None
    duration_s: float
    error_type: str | None       # RuntimeError / FileNotFoundError / NameError ...
    error_summary: str | None    # 错误首行
    error_line: int | None       # 从 traceback 提取的行号
    fix_hint: str                # 修复提示（按 error_type 模板生成）
    data_source: str             # "old" (15:29 报告) | "new" (本次新跑)
```

### 修复提示模板（按 error_type 分桶）
| error_type | 模板 |
|------------|------|
| `NameError` | `NameError: name 'X' is not defined` — 原因：变量被注释/未初始化。修复：在第 N 行附近加 `X = ...` |
| `RuntimeError: prefetch_factor` | `ValueError: prefetch_factor option could only be specified in multiprocessing` — 原因：PyTorch 2.x 严格化。修复：第 N 行 `DataLoader(..., prefetch_factor=2)` → 删 `prefetch_factor=2` |
| `RuntimeError: too many dimensions` | `ValueError: too many dimensions 'Series'` — 原因：pandas Series 直接喂 torch.tensor。修复：第 N 行 `torch.tensor(y_train)` → `torch.tensor(y_train.values)` |
| `RuntimeError: liblinear multiclass` | `liblinear solver does not support multiclass` — 原因：sklearn liblinear 不支持 3 分类。修复：第 N 行 `solver='liblinear'` → `solver='lbfgs'` |
| `RuntimeError: sheet too large` | `This sheet is too large` — 原因：to_excel 超 1048576 行。修复：第 N 行 `df.to_excel(...)` → `df.to_csv(...)` 或拆 sheet |
| `FileNotFoundError: kd_tree.m` | 模型未训练。修复：先跑 `kdtree_data.py` 生成 `../model/kd_tree.m` |
| `FileNotFoundError: hex/csv` | IMU 原始数据缺失。修复：把被试 hex 放到 `IMU_sleep_stage-.../data/` 或修改脚本读取路径 |
| `FileNotFoundError` (其他) | 检查路径文件是否存在；不存在就放数据，存在就检查 `Path(__file__)` 推导是否正确 |
| `ModuleNotFoundError` | `pip install <module>` |
| `timeout` | 训练耗时长。加长 timeout（如 600s）或减少数据量 |

行号提取：parse `error_detail` 中的 `line (\d+), in <module>` 正则。优先级：

1. `File "<绝对路径>", line N, in <module>` — 标准 Python traceback
2. `line N, in ana<...>` — 嵌套函数（analyze_data 之类）
3. 仅有一行 `NameError: name 'X' is not defined` 而无 traceback → 标 `error_line: None`，fix_hint 改为 "打开文件搜索 X 名称"
4. `ModuleNotFoundError: No module named 'X'` → 标 `error_line: None`

### "功能一句话"提取规则（按顺序回退）

1. 读取 module 顶部 docstring 的第一句（以 `.` `。` `!` `?` 结尾的首句）
2. 否则读 `if __name__ == "__main__":` 块内第一个非空、非注释的字符串字面量（通常是 print 参数）
3. 否则基于**文件名 + 顶层 import** 生成启发式：
   - 含 `train` → "训练 <算法> 模型"
   - 含 `deal`/`preprocess` → "数据预处理：<imports 中 sklearn/pandas 提示>"
   - 含 `extract` → "提取 <imports 提示> 数据"
   - 含 `chart`/`figure`/`imag` → "生成可视化图表"
   - 含 `test` → "测试/验证脚本"
   - 含 `count` → "统计/计数"
4. 兜底：`(无法推断功能)`

例：
- `kdtree_data.py` + `sklearn.neighbors` → 启发式 #3 → "训练 KD-Tree 用于分类"
- `bar_chart.py` + `matplotlib` → 启发式 #3 → "生成可视化图表"
- `descison_tree.py` 含 module docstring → 规则 #1

兜底情况：标 `purpose: "(无法推断)"`，**不假造**。

### 优先级分类

每脚本额外打 `priority` 标签。判定按以下优先级规则（**先匹配先赢**）：

1. ⚪ **P4-可忽略** — 全注释伪 .py（无 import + `comments_only=True`） 或无 main 且无 I/O 副作用（如 `model_figure.py` 单纯定义类）
2. 🔵 **P3-GPU** — 含 `torch` import + 训练循环（`for epoch in range(100)` 之类），需 GPU/长训练
3. 🟠 **P2-数据** — 失败原因是 `FileNotFoundError` 且目标文件非生成产物（`kd_tree.m` / `d0000003.txt` / 缺失 hex 等）
4. 🟢 **P0-快** — 失败原因可由 1-2 行代码改动修复（`NameError`/单参数删除/solver 替换等）
5. 🟡 **P1-中** — 其余（多行代码改动但无数据/GPU 依赖）

| priority | 判定 | 推荐处理 |
|----------|------|---------|
| 🟢 P0-快 | 1-2 行代码修复 | 现在修，~5 分钟 |
| 🟡 P1-中 | 多行代码修复 | 今天修，~30 分钟 |
| 🟠 P2-数据 | 缺数据/缺生成产物 | 数据到位后修 |
| 🔵 P3-GPU | DL 训练脚本 | 上服务器跑 |
| ⚪ P4-可忽略 | 无可执行代码/无 main | 视情况 |

## 数据流（end-to-end）

```
Step 1: tools/run_analysis.py --filter sleep_stage --timeout 120
        (29 个脚本 × 120s timeout 串行跑，~15 分钟)
        → 写 docs/superpowers/reports/run_results-sleep_stage.json
        → 终端打印实时进度（每脚本一行 summary）

Step 2: tools/generate_runnability_report.py
        (读两份 JSON + 静态扫描 48 个 .py 文件)
        → 写 docs/superpowers/reports/2026-06-06-script-runnability-report.md

Step 3: git add docs/superpowers/reports/2026-06-06-script-runnability-report.md \
            tools/generate_runnability_report.py \
            tools/run_results-sleep_stage.json \
            tools/run_analysis.py
        git commit -m "docs: 全量 48 脚本可运行性报告 + 新增 generate_runnability_report.py"
```

## 报告结构

`docs/superpowers/reports/2026-06-06-script-runnability-report.md`：

```markdown
# 脚本可运行性报告

- 运行时间: 2026-06-06 HH:MM
- 范围: graduation_transfer/ 48 个 .py 脚本（49 真实 - 1 跳过 = 48）
- 数据源: 5 旧（17:12 run_results.json，**不是 18**）+ 29 新（本次）+ 14 未跑（旧 sleep_classify 中无 17:12 JSON 数据）+ 1 漏网（`data_deal/test.py`）+ 1 跳过（feature_deal.py）
- 环境: master_study_env (Python 3.11, macOS ARM64, torch 2.12 CPU)

## 汇总

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 运行成功 | ? | ?% |
| ❌ 失败（runtime bug） | ? | ?% |
| ⏱ 超时 | ? | ?% |
| ❌ 失败（数据缺失） | ? | ?% |
| ❌ 失败（缺包） | ? | ?% |
| ❔ 未跑（缺数据） | 14 | 29% |
| ⚠️ 跳过 | 1 | 2% |
| **合计** | **48** | **100%** |

## 修复优先级

| 优先级 | 数量 | 处理建议 |
|--------|------|---------|
| 🟢 P0-快（5 分钟） | ? | 现在修 |
| 🟡 P1-中（30 分钟） | ? | 今天修 |
| 🟠 P2-长（需数据） | ? | 数据到位后修 |
| 🔵 P3-GPU | ? | 上服务器跑 |
| ⚪ P4-可忽略 | ? | 视情况 |

## 按子项目分节详述（48 条目，每条 ~15 行）
### sleep_classify（11 条）
#### ✅ descison_tree.py
- 路径: graduation_transfer/sleep_posture/sleep_classify/code/descison_tree.py
- 功能: 在 left/m/right 三类睡姿数据上训练决策树分类器
- Imports: pandas, sklearn.tree
- 运行: exit=0, 56.31s
- 结果: AUC = (0.993, 0.994, 0.992)
- 数据源: 旧 (17:12)

#### ❌ kdtree_data.py
- 路径: ...
- 功能: 训练 k-d tree 用于睡姿分类
- Imports: pandas, sklearn
- 运行: exit=1, 50.93s
- 错误: NameError: name 'Y' is not defined
- 行号: 41
- 修复: 取消第 41 行 `Y = new_df.iloc[:, -1]` 注释
- 优先级: 🟢 P0-快
- 数据源: 旧 (17:12)

### sleep_stage/IMU_sleep_stage-.../data_deal_code/（4 条）
### sleep_stage/IMU_sleep_stage-.../model/（7 条）
### sleep_stage/sleep_stage-迁移标签代码/code-.../（7 条，不含 __init__）
### sleep_stage/sleep_stage-迁移标签代码/model/（1 条）
### sleep_stage/Sleep-pdf处理代码/new_project/data_deal-.../（5 条，不含 feature_deal）
### sleep_stage/Sleep-pdf处理代码/new_project/model-.../（11 条）
### sleep_stage/Sleep-pdf处理代码/new_project/origin_data_deal/（2 条，不含 __init__）
### 跳过的脚本（1 条）
#### ⚠️ feature_deal.py
- 路径: ...
- 功能: （全注释伪 .py，136 行全部注释）
- 优先级: ⚪ P4-可忽略（建议删除或改为 .md）

## 附录
- 跑 29 个脚本的完整命令: `tools/run_analysis.py --filter sleep_stage`
- 重新生成本报告: `tools/generate_runnability_report.py`
- 旧 run_results.json: 17:12 5 条 sleep_classify 验证
- 旧 run-analysis-report.md: 15:29 18 个完整分析（markdown，无法结构化合并）
```

每条 ~15 行 × 48 条 ≈ 750 行 Markdown。报告本身可读性靠分组合并，不靠每条短。

## 错误处理

| 失败情形 | 处理 |
|---------|------|
| `tools/run_analysis.py --filter sleep_stage` 跑超时（29 脚本 × 120s 仍超时） | 终端报错，run_results-sleep_stage.json 写入已完成的 entries，generate_runnability_report.py 用"未完成"标 |
| `generate_runnability_report.py` 找不到新 JSON | 报错并提示先跑 `tools/run_analysis.py --filter sleep_stage` |
| 静态扫描 .py 读失败（编码） | 记录 `read_error`，标 `purpose: "(无法读取)"` |
| 静态扫描 ast.parse 失败 | 标 `purpose: "(语法错误)"`，跳过 docstring 提取 |
| 旧 JSON 缺字段（17:12 那 5 条缺一些字段） | 旧数据用 defensive get，新数据严格 |
| 修复提示模板无匹配 | 标 `fix_hint: "(手工诊断)"`，不假造 |
| 同名 stem 冲突（psg_rnn_lstm / test） | scan_all_scripts 用 rel_path 作 key 而非 path.stem，merge_results 三级回退（rel_path 精确 > 末段文件名 > label） |

## 验收

| 验收点 | 通过条件 |
|--------|---------|
| run_analysis.py 扩展后向后兼容 | 跑无参数 = 行为不变 |
| sleep_stage filter 工作 | `--filter sleep_stage` 发现恰好 29 个脚本（不含 `__init__.py`） |
| 29 个脚本都能进 run_results-sleep_stage.json | 文件存在，每脚本一条 entry |
| 报告覆盖 48 个 .py | `wc -l 报告 == ~750 行` |
| 失败脚本都有 error_line | 抽样 5 个，对照原文件行号正确 |
| 修复提示符合模板 | 抽样 5 个，文本与模板一致 |
| 优先级标签合理 | 5 个 P0 都是 1-2 行修改；P1 是多行；P3 是 GPU 训练 |
| 中文章段不乱码 | 报告中所有路径/标识符都是 UTF-8 |
| 不污染工作区 | `git status` 仅新文件出现在 `docs/superpowers/reports/` 和 `tools/` |
| 可重跑 | 删除 `run_results-sleep_stage.json`，重跑 `tools/run_analysis.py --filter sleep_stage` 重新生成 |
| 漏网脚本 `data_deal/test.py` 出现 | 报告中以 `❔ 未跑` 状态出现，标注"在磁盘但不在 SCRIPTS_ALL" |
| 旧 JSON 5 条都能 merge | `merge_results()` 输出 `matched 5/5`，无 WARN |

## 不做（YAGNI）

- 不修复任何 runtime bug（不在本计划范围）
- 不装 imblearn
- 不确认 sleep-cassette 数据来源
- 不重跑 sleep_classify 脚本
- 不重写 `run_analysis.py`（只增 filter + output 命名 + dry-run + print-output）
- 不写单元测试
- 不贴完整代码 diff
- 不估算工时/人天
- 不 `git push`
- 不合并 markdown 旧报告（15:29 报告信息无法结构化合并，只保留审计线索）

## 产出物

- `tools/run_analysis.py` — 扩展后版本（+60 行）
- `tools/generate_runnability_report.py` — 新建（~280 行）
- `docs/superpowers/reports/run_results-sleep_stage.json` — 29 脚本执行结果
- `docs/superpowers/reports/2026-06-06-script-runnability-report.md` — 48 脚本报告

## 决策记录

| 议题 | 担忧 | 采用决策 | 理由 |
|------|------|---------|------|
| 重跑全部 vs 只跑新 | 时间 15+ 分钟 | 只跑 29 个新修过的 | sleep_classify 状态稳定，5 条 JSON 已足够；18 条旧报告信息无法结构化合并 |
| 旧 JSON 改名 | 审计线索 | 不改名，新数据用后缀 | 17:12 5 条 JSON 留作审计线索 |
| 行号提取方式 | traceback 难 parse | 正则 `line (\d+), in <module>` | PyTorch/sklearn 错误格式统一 |
| 报告内文长度 | 太长 vs 太短 | 48 条 × ~15 行 ≈ 750 行 | 一行说清失败+原因+修复，便于扫读 |
| 修复提示要不要 diff | 详细 vs 简洁 | 不要 diff，只提示改哪里 | 已在脑暴阶段确认 |
| feature_deal.py | 算脚本吗 | 标 ⚪ P4 可忽略 | 136 行全注释，无可执行代码 |
| 优先级维度的数量 | 5 个够用 | 5 个：P0/P1/P2/P3/P4 | 与"修复工作量+数据依赖+GPU"维度对应 |
| 是否包含 untracked sleep_edf数据汇集/ | 是新数据 | 不包含 | 是数据目录，无 .py；不在脚本发现范围 |
| 同名 stem 处理 | dict key 冲突 | rel_path 作 key | psg_rnn_lstm / test 同名 100% 不会冲突 |
| importlib mock 验证 | 模块顶层副作用 | 改用 subprocess --dry-run | argparse sys.exit(2) 会污染 mock 上下文 |
| 漏网脚本 `data_deal/test.py` | 加 vs 不加 SCRIPTS_ALL | 不加 | 报告里以"❔ 未跑 + 在磁盘但不在 SCRIPTS_ALL"如实出现；保持 SCRIPTS_ALL 47 = 29 新 + 18 旧 不变 |
| 是否自动 git commit | 用户曾要求严格 | 准备命令但**不执行**，等用户确认 | 遵守 "不主动 commit" 约束 |

## 下一步

调用 `writing-plans` skill 把本设计转为逐步实施计划。
