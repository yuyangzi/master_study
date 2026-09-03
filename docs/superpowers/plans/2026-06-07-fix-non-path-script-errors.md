# 修复脚本非路径类运行错误 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 3 个非路径类失败脚本（PyTorch 兼容性 / 缺包 / 变量未定义），使其在 macOS + Python 3.11 环境正常运行

**Architecture:** 按风险从低到高逐个修复：先取消注释（kdtree_data.py），再删除无效参数（bp_algorithm.py），最后安装依赖包+防御性import（smote_label.py）。每个修复后立即验证。

**Tech Stack:** Python 3.11, PyTorch 2.12 CPU, pandas, scikit-learn, imbalanced-learn

---

## 文件结构

| 文件 | 操作 | 说明 |
|------|------|------|
| `graduation_transfer/sleep_posture/sleep_classify/code/kdtree_data.py:40` | 修改 | 取消 `Y = ...` 注释 |
| `graduation_transfer/sleep_posture/sleep_classify/code/bp_algorithm.py:134` | 修改 | 删除 `prefetch_factor=2`，临时修改 total_epoch=5 验证 |
| `graduation_transfer/sleep_stage/.../data_deal_code/smote_label.py:3,21` | 修改 | 添加 try/except 防御 |

### 已知问题（本次范围外）

- **标签编码不一致**: `kdtree_data.py` 使用 `{1: left, 2: m, 3: right}`，`bp_algorithm.py` 使用 `{0: left, 1: m, 2: right}`。已记录到 AGENTS.md，暂不修复。

---

## Task 0: 环境准备（安装缺失的 ML 包）

> venv 已存在（Python 3.11.15），只需安装 torch/sklearn/pandas 等缺失包。

- [ ] **Step 1: 安装依赖包**

```bash
cd /Users/zero/Desktop/master_study
./venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
./venv/bin/pip install pandas scikit-learn numpy tqdm imbalanced-learn openpyxl
```

- [ ] **Step 2: 验证环境可用**

```bash
./venv/bin/python3.11 -c "import torch, pandas, sklearn, imblearn; print('环境OK')"
```
Expected: 输出 "环境OK"

- [ ] **Step 3: 确认 3 个脚本以预期方式失败**

```bash
cd graduation_transfer/sleep_posture/sleep_classify/code
../../../../venv/bin/python3.11 kdtree_data.py 2>&1 | grep "NameError"
../../../../venv/bin/python3.11 bp_algorithm.py 2>&1 | grep "prefetch_factor"
```
Expected: 分别输出 NameError 和 prefetch_factor 相关错误

---

## Task 1: 修复 `kdtree_data.py` — 变量未定义（零风险）

**Files:**
- Modify: `graduation_transfer/sleep_posture/sleep_classify/code/kdtree_data.py:40`

- [ ] **Step 1: 取消第 40 行注释**

将第 40 行从：
```python
# Y = new_df.iloc[:, -1]
```
改为：
```python
Y = new_df.iloc[:, -1]
```

- [ ] **Step 2: 运行验证**

```bash
cd /Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code
timeout 120 ../../../../venv/bin/python3.11 kdtree_data.py
```
Expected: 完成训练，打印 `Accuracy:` / `Precision:` / `Recall:` / `F1-Score:`

- [ ] **Step 3: 检查 git diff（可选）**

```bash
cd /Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify
git diff code/kdtree_data.py
```
Expected: 显示第 40 行从注释变为有效代码

---

## Task 2: 修复 `bp_algorithm.py` — PyTorch 2.x 兼容（极低风险）

**Files:**
- Modify: `graduation_transfer/sleep_posture/sleep_classify/code/bp_algorithm.py:134`

- [ ] **Step 1: 删除第 134 行 `prefetch_factor=2`**

将第 125-135 行从：
```python
    train_dataloader = DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,
        shuffle=True,
        sampler=None,
        num_workers=0,
        collate_fn=None,
        pin_memory=False,
        drop_last=False,
        prefetch_factor=2
    )
```
改为：
```python
    train_dataloader = DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,
        shuffle=True,
        sampler=None,
        num_workers=0,
        collate_fn=None,
        pin_memory=False,
        drop_last=False,
    )
```

- [ ] **Step 2: 临时修改 total_epoch 为 5（用于验证）**

将第 149 行从：
```python
    total_epoch = 100
```
改为：
```python
    total_epoch = 5  # 临时验证用，完成后恢复为 100
```

- [ ] **Step 3: 运行验证**

```bash
cd /Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code
timeout 120 ../../../../venv/bin/python3.11 bp_algorithm.py
```
Expected: 不再报 RuntimeError，打印 `Accuracy:` 输出

- [ ] **Step 4: 恢复 total_epoch 为 100**

将第 149 行从：
```python
    total_epoch = 5  # 临时验证用，完成后恢复为 100
```
改回：
```python
    total_epoch = 100
```

- [ ] **Step 5: 检查 git diff（可选）**

```bash
cd /Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify
git diff code/bp_algorithm.py
```
Expected: 显示删除了 `prefetch_factor=2` 这一行，total_epoch 保持为 100

---

## Task 3: 修复 `smote_label.py` — 缺 imblearn 包（低风险）

**Files:**
- Modify: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/smote_label.py:3,21`

- [ ] **Step 1: 安装 imbalanced-learn 包**

```bash
cd /Users/zero/Desktop/master_study
./venv/bin/pip install imbalanced-learn
```

- [ ] **Step 2: 修改第 3 行 import 为防御性写法**

将第 1-4 行从：
```python
import os
import pandas as pd
from imblearn.over_sampling import SMOTE
from pathlib import Path
```
改为：
```python
import os
import pandas as pd
from pathlib import Path

try:
    from imblearn.over_sampling import SMOTE
    _HAS_SMOTE = True
except ImportError:
    SMOTE = None
    _HAS_SMOTE = False
```

- [ ] **Step 3: 在第 21 行使用前添加检查**

将第 21 行从：
```python
    smote = SMOTE(random_state=42, sampling_strategy={0: target_count})
```
改为：
```python
    if not _HAS_SMOTE:
        raise ImportError(
            "缺少依赖: imbalanced-learn。运行: pip install imbalanced-learn"
        )
    smote = SMOTE(random_state=42, sampling_strategy={0: target_count})
```

- [ ] **Step 4: 前置数据检查**

```bash
ls -la "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/base_data/liu_imu_label.csv"
```
Expected: 文件存在

- [ ] **Step 5: 运行验证**

```bash
cd "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code"
../../../../../../venv/bin/python3.11 smote_label.py
```
Expected: 生成 `base_data/liu_imu_label_smote_label0_100k.csv`

- [ ] **Step 6: 验证输出文件**

```bash
ls -la "../base_data/liu_imu_label_smote_label0_100k.csv"
```
Expected: 文件存在且大小合理

- [ ] **Step 7: 检查依赖冲突**

```bash
cd /Users/zero/Desktop/master_study
./venv/bin/pip check
```
Expected: 无冲突输出（或只有不影响的 warning）

---

## 验证汇总

所有修复完成后，运行完整验证：

```bash
# 起点：master_study 目录
cd /Users/zero/Desktop/master_study

# 验证 1: kdtree_data.py
cd graduation_transfer/sleep_posture/sleep_classify/code
timeout 120 ../../../../venv/bin/python3.11 kdtree_data.py
# 期望：打印 Accuracy:/Precision:/Recall:/F1-Score:

# 验证 2: bp_algorithm.py（已在 Task 2 中验证通过，跳过）
# 注：Task 2 已用 total_epoch=5 完成验证并恢复为 100，此处无需重复

# 验证 3: smote_label.py
cd "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code"
../../../../../../venv/bin/python3.11 smote_label.py
ls -la "../base_data/liu_imu_label_smote_label0_100k.csv"
# 期望：文件存在且大小合理
```

---

## 回退方案

如果任何修复引入新问题：

1. **kdtree_data.py**: 重新注释第 40 行 `Y = ...`
2. **bp_algorithm.py**: 恢复 `prefetch_factor=2` 行，恢复 `total_epoch = 100`
3. **smote_label.py**: 恢复原始 import，卸载 imbalanced-learn

---

## 成功标准

- [ ] 3 个脚本在本地环境下能跑通主流程（带超时保护）
- [ ] 不破坏已有功能（`fix_paths.py` 修复的路径、其他依赖）
- [ ] 修改可被 `git diff` 清楚看到（`sleep_classify/` 在 git 下）
- [ ] `total_epoch` 在验证后恢复为 100（bp_algorithm.py）
