# 更新 2026-06-06 脚本可运行性报告 — 设计

**日期：** 2026-06-07
**任务：** 根据 2026-06-07 修复的 3 个非路径类脚本，更新 docs/superpowers/reports/2026-06-06-script-runnability-report.md

**关联 plan：** docs/superpowers/plans/2026-06-07-fix-non-path-script-errors.md（已完成，commit 7c45397）

---

## 范围

仅 5 处修改。**不重跑任何脚本**，不修改未涉及脚本的状态。

## 设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 更新范围 | 增量：3 条脚本 + 汇总 + 头部 | 用户选择；未跑脚本保持"修复前"历史快照 |
| smote_label.py 状态 | 仍为 ❌，更新错误信息 | 用户选择；与原状态类型一致 |
| 优先级调整 | bp_algorithm.py P3→P4 | 用户选择；修复后 CPU 可跑，无需 GPU |
| 环境字段 | master_study_env → venv（保持简洁） | 用户选择；保持原描述风格 |
| 汇总数字 | ✅ 17→19, ❌ 9→7 | 用户选择；kdtree + bp_algorithm 进入成功 |
| 头部元信息 | 加 "更新: 2026-06-07" 一行 | 用户选择；最小改动 |

## 5 处具体修改

### 1. 头部元信息
```diff
 - 运行时间: 2026-06-06
+- 更新: 2026-06-07 — 修复 3 个非路径脚本（kdtree_data/bp_algorithm/smote_label），
+-        plan: docs/superpowers/plans/2026-06-07-fix-non-path-script-errors.md
 - 范围: graduation_transfer/ 48 个 .py 脚本（49 个真实脚本 - 1 跳过 = 48；额外 1 条 `data_deal/test.py` 在磁盘但不在 SCRIPTS_ALL）
 - 数据源: 5 旧 (17:12 run_results.json) + 29 新 (本次) + 14 未跑 + 1 跳过（feature_deal.py）
-- 环境: master_study_env (Python 3.11, macOS ARM64, torch 2.12 CPU)
+- 环境: venv (Python 3.11, macOS ARM64, torch 2.12 CPU)
```

### 2. 汇总表
| 状态 | 原 | 新 |
|---|---|---|
| ✅ 运行成功 | 17 | **19** |
| ❌ 失败 | 9 | **7** |
| ⏱ 超时 | 8 | 8 |
| ⚠️ 跳过 | 1 | 1 |

### 3. 修复优先级表
| 优先级 | 原 | 新 |
|---|---|---|
| 🟢 P0-快 | 0 | 0 |
| 🟡 P1-中 | 17 | 17 |
| 🟠 P2-数据 | 2 | 2 |
| 🔵 P3-GPU | 4 | **3** |
| ⚪ P4-可忽略 | 25 | **26** |

### 4. 三条目标脚本

**`kdtree_data.py`** (line 74-84): ❌→✅, ⚪ P4 不变
- 删除"错误"和"修复"字段（已修复）
- 状态/优先级/数据源字段保持
- "运行"字段更新为 2026-06-07 验证数据：
  - `运行: exit=0, X.Xs; 修复 line 40 取消 Y 注释; Acc=1.00`
- 标题从 `#### ❌` 改 `#### ✅`

**`bp_algorithm.py`** (line 40-53): ❌→✅, 🔵 P3→⚪ P4
- 删除"错误"和"修复"字段
- "运行"更新为 2026-06-07 验证：
  - `运行: exit=0, X.Xs; 修复 line 134 删除 prefetch_factor=2; 5 epochs Acc=0.987 (已恢复 total_epoch=100)`
- 标题从 `#### ❌` 改 `#### ✅`

**`smote_label.py`** (line 235-245): ❌→❌, 🟡 P1 不变
- "错误"字段：ModuleNotFoundError → ValueError SMOTE 降采样失败
- "修复"字段：缺包 → 部分修复
- 标题保持 `#### ❌`
- 优先级保持 🟡 P1-中（数据逻辑 bug 仍需后续处理）
- 修复描述：`部分修复：defensive import（line 5-10 + 27-30）; 数据逻辑 bug 未修 (SMOTE 只能过采样，class 0 有 1.35M 样本，目标 100k 需用 RandomUnderSampler)`

### 5. 附录
在"跑 29 个脚本"命令旁加一行：
```
- 2026-06-07 plan 修复 3 条：kdtree_data/bp_algorithm/smote_label（commit 7c45397）
```

## 保留不变

- 报告标题
- 范围说明
- 14 条未跑脚本（仍标 ❔）
- 8 条超时（仍标 ⏱）
- 1 条跳过（feature_deal.py）
- 其他 42 条脚本详情
- 附录其他命令
- bp_algorithm.py 错误堆栈中的 `master_study_env/lib/.../dataloader.py` 路径（line 48）
  - 原因：修复后整个"错误"字段会被删除（改为 ✅），该路径自然消失

## grill-me 决策记录

| # | 模糊点 | 决策 |
|---|--------|------|
| 1 | 错误堆栈中 master_study_env 路径 | 保留作历史快照（修复后整段删除） |
| 2 | bp_algorithm.py 修复行号 | 运行字段加"修复 line 134" |
| 3 | kdtree_data.py 修复行号 | 运行字段加"修复 line 40" |
| 4 | smote_label 修复措辞 | "部分修复：defensive import...数据逻辑 bug 未修" |
| 5 | 运行字段格式 | 标准格式（exit + 耗时 + 修复 + 指标，逗号/分号分隔） |
| 6 | smote_label 优先级 | 保持 🟡 P1-中 |

## 验证

修改完成后：
1. `git diff` 检查仅 5 处变更
2. 头/汇总/优先级 3 个表数字自洽：
   - 总数 = 19 + 7 + 8 + 1 = 35（基础 29 跑 + 5 旧 + 1 跳过，与原 35 一致；剩余 14 ❔ 未跑，总 49 = 48 + 1 隐藏）
3. 优先级总数：0+17+2+3+26 = 48 ✓
4. 3 条目标脚本的状态、错误、修复、运行字段一致性
