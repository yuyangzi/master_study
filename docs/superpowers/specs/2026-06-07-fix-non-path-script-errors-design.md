# 修复脚本非路径类运行错误 — 设计文档

- 日期: 2026-06-07（v2 - 含 Metis 审查修正）
- 范围: `graduation_transfer/` 下 3 个非路径类失败脚本
- 来源: `docs/superpowers/reports/2026-06-06-script-runnability-report.md`
- 目标: 最小修改、风险最低地修复 3 个失败脚本（PyTorch 兼容性 / 缺包 / 变量未定义），使其在 macOS + Python 3.11 环境正常运行

## 背景 & 上下文

经 `tools/fix_paths.py` 跑过后，**Windows 路径硬编码问题（30 个文件）已全部修复**。当前剩余的脚本失败原因已收敛为 3 类非路径问题：

| 失败脚本 | 错误类型 | 行号 | 报告优先级 |
|---------|---------|------|-----------|
| `bp_algorithm.py` | PyTorch 2.x RuntimeError | 134 | 🔵 P3-GPU |
| `smote_label.py` | ModuleNotFoundError (`imblearn`) | 3 | 🟡 P1-中 |
| `kdtree_data.py` | NameError (`Y`) | 43 | ⚪ P4-可忽略 |

### 已知问题（本次范围外）

- **标签编码不一致**：`kdtree_data.py` 使用 `{1: left, 2: m, 3: right}`，`bp_algorithm.py` 使用 `{0: left, 1: m, 2: right}`
- `kdtree_data.py` 无 `if __name__ == "__main__"` 保护，导入时会执行全部代码

> **不在本次范围**：
> - 数据文件缺失（8 个脚本，需用户提供数据）
> - GPU/服务器训练（4 个脚本，运行环境限制）
> - 报告未跑/未标注的 14 个脚本
> - `feature_deal.py`（全注释）

## 约束

- **修改最小化**：每个修复 ≤ 5 行代码改动
- **零副作用**：不修改 `fix_paths.py`、不重新生成报告
- **现有模式保持**：路径已用 `pathlib.Path(__file__).parent`，继续沿用
- **防御性编程**：依赖包改动加 try/except，避免再次 ImportError 崩溃
- **环境**: macOS ARM64, Python 3.11, torch 2.12 CPU
- **Git 策略**: `sleep_classify/` 有独立 git 仓库（分支 `release.new`），修改后视情况提交；`sleep_stage/` 不在 git 下

---

## 步骤 0: 环境准备（P0 阻塞项）

> ⚠️ **Metis 审查发现**：`master_study_env` 已被删除，`venv/` 是空壳。所有验证步骤都会因缺少 torch/sklearn/pandas 而失败。

### 方案 A: 本地重建（推荐）

```bash
# 1. 重建 conda/venv 环境
cd /Users/zero/Desktop/master_study
python -m venv master_study_env
source master_study_env/bin/activate

# 2. 安装依赖（torch CPU 版本）
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install pandas scikit-learn numpy tqdm imbalanced-learn openpyxl

# 3. 验证
python -c "import torch, pandas, sklearn; print('环境OK')"
```

### 方案 B: 委托远程

如果本地环境重建困难，将验证委托给远程服务器 `root@159.75.177.109` 或 PyCharm `Python 3.7 (pytorch)` 环境。

### 前置验证

环境准备好后，先确认 3 个脚本以预期方式失败：
```bash
cd graduation_transfer/sleep_posture/sleep_classify/code
python kdtree_data.py 2>&1 | grep "NameError"
python bp_algorithm.py 2>&1 | grep "prefetch_factor"
```

---

## 修复 1: `bp_algorithm.py` — PyTorch 2.x 兼容

### 文件位置
`graduation_transfer/sleep_posture/sleep_classify/code/bp_algorithm.py`

### 错误
```
ValueError: prefetch_factor option could only be specified in dataloader with num_workers > 0
```

### 根因
PyTorch 2.x 规范：`prefetch_factor` 仅在 `num_workers > 0` 时生效。当前 `num_workers=0`，该参数本就不起作用，且会触发 ValueError。

### 改动（1 行删除）
**文件**：`bp_algorithm.py` 第 134 行

**删除**：
```python
        prefetch_factor=2
```

**修改后**：
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

### 验证
```bash
cd /Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code
timeout 120 python bp_algorithm.py
```
- 期望：不再报 RuntimeError，打印 `Accuracy:` 输出
- 超时：120 秒（报告记录 100 秒）

---

## 修复 2: `smote_label.py` — 缺 imblearn 包

### 文件位置
`graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/smote_label.py`

### 错误
```
ModuleNotFoundError: No module named 'imblearn'
```

### 根因
本地 `master_study_env` 未安装 `imbalanced-learn`（即 `imblearn`）包。

### 改动（2 步）

**步骤 1**：命令行执行
```bash
/Users/zero/Desktop/master_study/venv/bin/pip install imbalanced-learn
```

> 注：PyPI 包名为 `imbalanced-learn`，pip install 后 import 用 `imblearn`。

**步骤 2**：第 3 行 import 改为防御性写法

**修改前**：
```python
import os
import pandas as pd
from imblearn.over_sampling import SMOTE
from pathlib import Path
```

**修改后**：
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

**步骤 3**：第 21 行使用前加检查

**修改前**：
```python
    smote = SMOTE(random_state=42, sampling_strategy={0: target_count})
```

**修改后**：
```python
    if not _HAS_SMOTE:
        raise ImportError(
            "缺少依赖: imbalanced-learn。运行: pip install imbalanced-learn"
        )
    smote = SMOTE(random_state=42, sampling_strategy={0: target_count})
```

### 验证
```bash
# 前置检查：数据文件存在
ls -la "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/base_data/liu_imu_label.csv"

# 执行修复后的脚本
cd "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code"
python smote_label.py

# 验证输出
ls -la "../base_data/liu_imu_label_smote_label0_100k.csv"
```
- 期望：生成 `base_data/liu_imu_label_smote_label0_100k.csv`
- 检查依赖冲突：`pip check`

---

## 修复 3: `kdtree_data.py` — 变量未定义

### 文件位置
`graduation_transfer/sleep_posture/sleep_classify/code/kdtree_data.py`

### 错误
```
NameError: name 'Y' is not defined
```

### 根因
第 40 行 `Y = new_df.iloc[:, -1]` 被错误注释掉，导致第 43 行 `train_test_split(X, Y, ...)` 引用未定义的 `Y`。

### 改动（1 行取消注释）

**文件**：`kdtree_data.py` 第 40 行

**修改前**：
```python
# 3. 根据需求获取最原始的特征属性矩阵X和目标属性Y
X = new_df.iloc[:, :-1]
# print(X.shape)
# Y = new_df.iloc[:, -1]
```

**修改后**：
```python
# 3. 根据需求获取最原始的特征属性矩阵X和目标属性Y
X = new_df.iloc[:, :-1]
# print(X.shape)
Y = new_df.iloc[:, -1]
```

### 验证
```bash
cd /Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code
timeout 120 python kdtree_data.py
```
- 期望：完成训练，打印 `Accuracy:` / `Precision:` / `Recall:` / `F1-Score:`
- 超时：120 秒

---

## 实施顺序

按修复风险从低到高：

1. **修复 3**（`kdtree_data.py`，1 行取消注释，零风险）
2. **修复 1**（`bp_algorithm.py`，1 行删除，极低风险）
3. **修复 2**（`smote_label.py`，先 `pip install` 再改 2 处代码）

每个修复完成后立即验证，确保问题解决再进行下一个。

## 风险评估

| 修复 | 风险 | 回退难度 |
|------|------|---------|
| 修复 1 | 极低（删除无效参数） | 极低（恢复 1 行） |
| 修复 2 | 低（仅 import + 1 行检查） | 极低（恢复原 import） |
| 修复 3 | 极低（恢复被注释代码） | 极低（重新注释） |

## 成功标准

- **环境前提**: torch, pandas, sklearn, numpy, imbalanced-learn 已安装
- 3 个脚本在本地环境下能跑通主流程（带超时保护）
- 不破坏已有功能（`fix_paths.py` 修复的路径、其他依赖）
- 修改可被 `git diff` 清楚看到（`sleep_classify/` 在 git 下，`sleep_stage/` 不在）

## 附录: Metis 审查要点

| 问题 | 严重性 | 处理 |
|------|--------|------|
| 环境不存在 | P0 | 添加步骤 0：环境准备 |
| 验证需 `cd` 命令 | P2 | 已在验证中添加 |
| `bp_algorithm.py` 需超时 | P2 | 已添加 timeout 120 |
| `smote_label.py` 前置数据检查 | P2 | 已添加 ls 检查 |
| 嵌套 git 提交策略 | P3 | 记录在约束中 |
| 标签编码不一致 | P4 | 记录在已知问题 |
