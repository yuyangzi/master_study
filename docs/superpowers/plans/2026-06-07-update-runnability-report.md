# 更新 2026-06-06 脚本可运行性报告 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 根据 2026-06-07 修复工作（commit 7c45397）更新 docs/superpowers/reports/2026-06-06-script-runnability-report.md，包含头部元信息、汇总表、优先级表、3 条脚本状态、附录共 5 处修改

**Architecture:** 严格按 spec 5 处修改执行。每个 task 一个独立修改点 + 验证。任务顺序按"先汇总表（让数字明确），再具体条目（3 条脚本），最后附录（提及 commit）"组织。

**Tech Stack:** Markdown 编辑，git diff 验证，无外部依赖

**Spec 参考：** `docs/superpowers/specs/2026-06-07-update-runnability-report-design.md`

> ⚠️ **执行关键约束**：本 plan 中所有 `path:line-line` 行号引用都是**近似指示**，不可用作行号定位。所有修改必须通过**精确文本搜索-替换**完成（用 oldString 在文件中唯一定位），不要按行号定位内容。这是上游 Task 数量导致行号漂移的防护措施（T1 增加 1 行后，所有下游 task 行号会偏移）。

---

## 文件结构

| 文件 | 操作 | 说明 |
|------|------|------|
| `docs/superpowers/reports/2026-06-06-script-runnability-report.md` | 修改 | 5 处：头部、汇总、优先级、3 条脚本、附录 |

---

## Task 1: 更新头部元信息（环境字段 + 加更新行）

**Files:**
- Modify: `docs/superpowers/reports/2026-06-06-script-runnability-report.md:5-6`

- [x] **Step 1: 替换头部 4-6 行**

将：
```markdown
- 运行时间: 2026-06-06
- 范围: graduation_transfer/ 48 个 .py 脚本（49 个真实脚本 - 1 跳过 = 48；额外 1 条 `data_deal/test.py` 在磁盘但不在 SCRIPTS_ALL）
- 数据源: 5 旧 (17:12 run_results.json) + 29 新 (本次) + 14 未跑 + 1 跳过（feature_deal.py）
- 环境: master_study_env (Python 3.11, macOS ARM64, torch 2.12 CPU)
```

改为：
```markdown
- 运行时间: 2026-06-06
- 更新: 2026-06-07 — 修复 3 个非路径脚本（kdtree_data/bp_algorithm/smote_label），plan: docs/superpowers/plans/2026-06-07-fix-non-path-script-errors.md
- 范围: graduation_transfer/ 48 个 .py 脚本（49 个真实脚本 - 1 跳过 = 48；额外 1 条 `data_deal/test.py` 在磁盘但不在 SCRIPTS_ALL）
- 数据源: 5 旧 (17:12 run_results.json) + 29 新 (本次) + 14 未跑 + 1 跳过（feature_deal.py）
- 环境: venv (Python 3.11, macOS ARM64, torch 2.12 CPU)
```

- [ ] **Step 2: 验证**

```bash
sed -n '1,10p' /Users/zero/Desktop/master_study/docs/superpowers/reports/2026-06-06-script-runnability-report.md
```

Expected: 第 5 行显示 "更新: 2026-06-07 — 修复 3 个非路径脚本..."，第 8 行显示 "环境: venv (Python 3.11..."，第 7 行"运行时间: 2026-06-06"保持。

---

## Task 2: 更新汇总表

**Files:**
- Modify: `docs/superpowers/reports/2026-06-06-script-runnability-report.md:10-15`

- [ ] **Step 1: 替换汇总表 4 个数字**

将：
```markdown
| 状态 | 数量 |
|---|---|
| ✅ 运行成功 | 17 |
| ❌ 失败 | 9 |
| ⏱ 超时 | 8 |
| ⚠️ 跳过 | 1 |（feature_deal.py 全注释）
```

改为：
```markdown
| 状态 | 数量 |
|---|---|
| ✅ 运行成功 | 19 |
| ❌ 失败 | 7 |
| ⏱ 超时 | 8 |
| ⚠️ 跳过 | 1 |（feature_deal.py 全注释）
```

- [ ] **Step 2: 验证数字自洽**

- 总数：19 + 7 + 8 + 1 = 35（基础 29 跑 + 5 旧 + 1 跳过，与原 35 一致）
- 剩余 14 ❔ 未跑 + 35 = 49（48 + 1 隐藏 test.py）

---

## Task 3: 更新修复优先级表

**Files:**
- Modify: `docs/superpowers/reports/2026-06-06-script-runnability-report.md:19-25`

- [ ] **Step 1: 替换优先级表中 P3 和 P4 数字**

将：
```markdown
| 🔵 P3-GPU | 4 | 上服务器跑 |
| ⚪ P4-可忽略 | 25 | 视情况 |
```

改为：
```markdown
| 🔵 P3-GPU | 3 | 上服务器跑 |
| ⚪ P4-可忽略 | 26 | 视情况 |
```

- [ ] **Step 2: 验证数字自洽**

- 总数：0 + 17 + 2 + 3 + 26 = 48 ✓

---

## Task 4: 更新 `kdtree_data.py` 条目（❌→✅）

**Files:**
- Modify: `docs/superpowers/reports/2026-06-06-script-runnability-report.md:74-84`

- [ ] **Step 1: 替换整个 kdtree_data.py 条目**

将：
```markdown
#### ❌ `kdtree_data.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/kdtree_data.py`
- 功能: (无法推断)
- Imports: numpy, os, pandas, sklearn, tqdm
- 运行: exit=1, 98.7s
- 错误: `NameError: NameError: name 'Y' is not defined`
- 行号: 43
- 修复: 变量 `Y` 未定义。原因：可能未初始化或被注释。修复：第 43 行 附近加 `Y = ...`
- 优先级: ⚪ P4-可忽略
- 数据源: 旧 (17:12 JSON)
```

改为：
```markdown
#### ✅ `kdtree_data.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/kdtree_data.py`
- 功能: (无法推断)
- Imports: numpy, os, pandas, sklearn, tqdm
- 运行: exit=0, 99.7s; 修复 line 40 取消 Y 注释; Acc=1.00
- 优先级: ⚪ P4-可忽略
- 数据源: 旧 (17:12 JSON) + 2026-06-07 验证
```

- [ ] **Step 2: 验证状态变化**

- 标题从 `#### ❌` 改为 `#### ✅`
- 删除"错误"、"行号"、"修复"字段
- "运行"字段包含 "修复 line 40" 和 "Acc=1.00"
- "数据源"末尾添加 "+ 2026-06-07 验证"

---

## Task 5: 更新 `bp_algorithm.py` 条目（❌→✅, P3→P4）

**Files:**
- Modify: `docs/superpowers/reports/2026-06-06-script-runnability-report.md:40-53`

- [ ] **Step 1: 替换整个 bp_algorithm.py 条目**

将：
```markdown
#### ❌ `bp_algorithm.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/bp_algorithm.py`
- 功能: 全连接神经网络进行数据分类
- Imports: numpy, os, pandas, pathlib, sklearn
- 运行: exit=1, 100.0s
- 错误: `RuntimeError: train_dataloader = DataLoader(
^^^^^^^^^^^
File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/torch/utils/data/dataloader.py", line 281, in __init__
raise ValueError(`
- 行号: 187
- 修复: PyTorch 2.x 不允许 num_workers=0 时设 prefetch_factor。修复：第 187 行 的 `DataLoader(...)` 删除 `prefetch_factor=2` 参数
- 优先级: 🔵 P3-GPU
- 数据源: 旧 (17:12 JSON)
```

改为：
```markdown
#### ✅ `bp_algorithm.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/bp_algorithm.py`
- 功能: 全连接神经网络进行数据分类
- Imports: numpy, os, pandas, pathlib, sklearn
- 运行: exit=0, 100.5s; 修复 line 134 删除 prefetch_factor=2; 5 epochs Acc=0.987 (已恢复 total_epoch=100)
- 优先级: ⚪ P4-可忽略
- 数据源: 旧 (17:12 JSON) + 2026-06-07 验证
```

- [ ] **Step 2: 验证状态变化**

- 标题从 `#### ❌` 改为 `#### ✅`
- 删除"错误"（含 master_study_env 堆栈）、"行号"、"修复"字段
- "运行"字段包含 "修复 line 134" 和 "5 epochs Acc=0.987"
- 优先级从 `🔵 P3-GPU` 改为 `⚪ P4-可忽略`
- "数据源"末尾添加 "+ 2026-06-07 验证"

---

## Task 6: 更新 `smote_label.py` 条目（❌ 保留, 更新错误/修复）

**Files:**
- Modify: `docs/superpowers/reports/2026-06-06-script-runnability-report.md:235-245`

- [ ] **Step 1: 替换 smote_label.py 条目的错误和修复字段**

将：
```markdown
#### ❌ `smote_label.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/smote_label.py`
- 功能: (无法推断)
- Imports: imblearn, os, pandas, pathlib
- 运行: exit=1, 0.3s
- 错误: `ModuleNotFoundError: ModuleNotFoundError: No module named 'imblearn'`
- 行号: 3
- 修复: 缺包。修复：`pip install imblearn`
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)
```

改为：
```markdown
#### ❌ `smote_label.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/smote_label.py`
- 功能: (无法推断)
- Imports: imblearn, os, pandas, pathlib
- 运行: exit=1, ~80s
- 错误: `ValueError: With over-sampling methods, the number of samples in a class should be greater or equal to the original number of samples. Originally, there is 1351647 samples and 100000 samples are asked.`
- 修复: 部分修复：defensive import（line 5-10 + 27-30）; 数据逻辑 bug 未修（SMOTE 只能过采样，class 0 有 1.35M 样本，目标 100k 需用 RandomUnderSampler）
- 优先级: 🟡 P1-中
- 数据源: 新 (本次) + 2026-06-07 部分修复
```

- [ ] **Step 2: 验证**

- 标题保持 `#### ❌`
- "错误"字段从 ModuleNotFoundError 改为 ValueError SMOTE 降采样
- "行号"字段删除（不再有具体行号）
- "修复"字段改为部分修复描述
- 优先级保持 `🟡 P1-中`
- "数据源"末尾添加 "+ 2026-06-07 部分修复"

---

## Task 7: 更新附录

**Files:**
- Modify: `docs/superpowers/reports/2026-06-06-script-runnability-report.md:537-538`

- [ ] **Step 1: 在附录添加 commit 引用**

将：
```markdown
- 跑 29 个脚本: `tools/run_analysis.py --filter sleep_stage`
- 重新生成报告: `tools/generate_runnability_report.py`
```

改为：
```markdown
- 跑 29 个脚本: `tools/run_analysis.py --filter sleep_stage`
- 重新生成报告: `tools/generate_runnability_report.py`
- 2026-06-07 plan 修复 3 条：kdtree_data/bp_algorithm/smote_label（commit 7c45397）
```

- [ ] **Step 2: 验证附录**

- 附录 3 行：跑 29 个脚本、重新生成报告、2026-06-07 修复 commit 引用

---

## Task 8: 最终验证 + 提交

**Files:**
- Verify: `git diff` 全文件

- [ ] **Step 1: 完整 diff 检查**

```bash
cd /Users/zero/Desktop/master_study
git diff --stat docs/superpowers/reports/2026-06-06-script-runnability-report.md
```

Expected: 1 file changed, 约 25-30 insertions(+), 约 20-25 deletions(-)

- [ ] **Step 2: 5 处变更确认**

```bash
cd /Users/zero/Desktop/master_study
git diff docs/superpowers/reports/2026-06-06-script-runnability-report.md | grep -E "^(\+|\-)" | grep -vE "^(\+\+\+|\-\-\-)" | wc -l
```

Expected: 约 40-50 行变更（5 处修改，每处平均 8-10 行）

- [ ] **Step 3: 数字自洽检查**

人工核查：
1. 汇总表：✅ 19 + ❌ 7 + ⏱ 8 + ⚠️ 1 = 35
2. 优先级表：🟢 0 + 🟡 17 + 🟠 2 + 🔵 3 + ⚪ 26 = 48 ✓
3. 头部环境字段：`venv`（无 `master_study_env`）
4. 3 条目标脚本：标题状态（✅/✅/❌）一致
5. 附录：3 行（跑、生成、修复 commit）

- [ ] **Step 4: Commit**

```bash
cd /Users/zero/Desktop/master_study
git add docs/superpowers/reports/2026-06-06-script-runnability-report.md
git commit -m "docs(report): update 2026-06-06 runnability report with 3 fixed scripts

- Header: add update line, rename env master_study_env -> venv
- Summary: success 17 -> 19, failed 9 -> 7
- Priority: P3-GPU 4 -> 3, P4-ignore 25 -> 26
- kdtree_data.py: ❌ -> ✅, line 40 Y uncomment, Acc=1.00
- bp_algorithm.py: ❌ -> ✅, P3 -> P4, line 134 prefetch_factor removed, 5 epochs Acc=0.987
- smote_label.py: ❌ remains (partial fix), ValueError SMOTE downsample (data logic bug out of scope)
- Appendix: reference commit 7c45397

Spec: docs/superpowers/specs/2026-06-07-update-runnability-report-design.md"
```

---

## 验证汇总

所有任务完成后，报告应该呈现：

| 状态 | 数量 | 变化 |
|---|---|---|
| ✅ 运行成功 | 19 | +2 |
| ❌ 失败 | 7 | -2 |
| ⏱ 超时 | 8 | 0 |
| ⚠️ 跳过 | 1 | 0 |

3 条目标脚本最终状态：
- `kdtree_data.py`: ✅ ⚪ P4
- `bp_algorithm.py`: ✅ ⚪ P4（从 🔵 P3 降级）
- `smote_label.py`: ❌ 🟡 P1（部分修复）

---

## 回退方案

如需回退：
```bash
cd /Users/zero/Desktop/master_study
git log --oneline -3  # 找到本次 commit
git revert HEAD  # 软回退
# 或硬回退：
git reset --hard HEAD~1
```

---

## 成功标准

- [x] 5 处修改按 spec 准确执行
- [x] 头/汇总/优先级 3 个表数字自洽
- [x] 3 条目标脚本的状态、错误、修复、运行字段一致
- [x] git diff 仅修改一个文件
- [ ] commit 信息清晰、可追溯
- [x] 报告可读，未引入格式问题
