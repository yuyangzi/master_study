# Python 脚本运行分析报告

- 运行时间: 2026-06-06 15:28:35
- 运行环境: master_study_env（Python 3.11, macOS ARM64）
- 运行工具: tools/run_analysis.py
- 总脚本数: 18

## 汇总

| 分类 | 数量 | 占比 |
|---|---|---|
| ✅ 运行成功 | 7 | 38.9% |
| ⏱ 超时（部分完成） | 1 | 5.6% |
| ❌ NameError（变量未定义） | 1 | 5.6% |
| ❌ FileNotFoundError（数据文件缺失） | 3 | 16.7% |
| ❌ ModuleNotFoundError（模块缺失） | 0 | 0.0% |
| ❌ 其他运行时错误 | 6 | 33.3% |
| ❌ 文件不存在 | 0 | 0.0% |
| **合计失败** | **11** | **61.1%** |

---
## ✅ 运行成功

| 脚本 | 耗时 | 输出摘要 |
|---|---|---|
| `bar_chart` | 1.01s | RNN             88.50       % 88.46       % 88.64       % 88.52       % | LSTM            84.19       % 84.10       % 84.35       % 84.20       % | RN |
| `descison_tree` | 56.31s | 训练数据Y的数据类型:<class 'pandas.Series'> | Y的取值范围:[0 1 2] | auc:(0.9928420496024226, 0.993542677423739, 0.9916288158580131) |
| `kmeans_algorithm` | 52.06s | Adjusted Rand Index: 0.09632524847063463 |
| `model_figure` | 1.15s | (无输出) |
| `new__hybird_imag` | 0.87s | (无输出) |
| `serial_port_extract` | 0.01s | 错误: [Errno 2] could not open port COM5: [Errno 2] No such file or directory: 'COM5' |
| `test_psg_data` | 4.43s | NOTE: pick_channels() is a legacy function. New code should use inst.pick(...). | ECG:[1.11022302e-19 1.11022302e-19 1.11022302e-19 ... 7.44239280e-04 |

---
## ⏱ 超时（部分完成）

以下脚本在设定的 timeout 内未执行完毕，但已产生部分输出。
如需要完整结果，可加长 timeout 或在有 GPU 的服务器上运行。

| 脚本 | 超时(s) | 已耗时 | 末行输出 |
|---|---|---|---|
| `SVM_algorithm` | 120s | 120.04s | `` |

---
## ❌ NameError（变量未定义）

这些脚本存在变量未定义的 bug，并非环境问题。

### `kdtree_data`

- **耗时**: 50.93s
- **错误**: `NameError: name 'Y' is not defined`
- **stdout**:
```
(无)
```
- **stderr**:
```
progress file:   0%|          | 0/87 [00:00<?, ?it/s]
progress file:   1%|          | 1/87 [00:00<00:57,  1.49it/s]
progress file:   2%|▏         | 2/87 [00:01<00:54,  1.56it/s]
progress file:   3%|▎         | 3/87 [00:01<00:52,  1.59it/s]
progress file:   5%|▍         | 4/87 [00:02<00:42,  1.97it/s]
progress file:   6%|▌         | 5/87 [00:02<00:42,  1.93it/s]
progress file:   7%|▋         | 6/87 [00:03<00:44,  1.80it/s]
progress file:   8%|▊         | 7/87 [00:03<00:45,  1.75it/s]
progress fil
```


---
## ❌ FileNotFoundError（数据文件缺失）

这些脚本引用了本地不存在的文件（硬编码 Windows 路径或本地数据文件缺失）。

### `origin_test`

- **耗时**: 0.2s
- **错误**: `FileNotFoundError: [Errno 2] No such file or directory: 'd0000087.txt'`
- **stderr**:
```
Traceback (most recent call last):
  File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/test.py", line 176, in <module>
    analyze_data(file_path, start_time=130, end_time=190)  # 选择从 0 到 10 秒的数据进行分析
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/test.py", line 147, in ana
```

### `test_all`

- **耗时**: 0.19s
- **错误**: `FileNotFoundError: [Errno 2] No such file or directory: 'd0000003.csv'`
- **stderr**:
```
Traceback (most recent call last):
  File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/test_all.py", line 153, in <module>
    raw_data = read_hex_data_from_txt(file_path)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/test_all.py", line 8, in read_hex_data_from_txt
    with open
```

### `verify_model`

- **耗时**: 0.19s
- **错误**: `FileNotFoundError: [Errno 2] No such file or directory: '../model/kd_tree.m'`
- **stderr**:
```
Traceback (most recent call last):
  File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code/verify_model.py", line 20, in <module>
    kd_tree = joblib.load("../model/kd_tree.m")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/joblib/numpy_pickle.py", line 735, in load
    with open(filename, "rb") as f:
         ^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such fi
```


---
## ❌ ModuleNotFoundError（模块缺失）

无

---
## ❌ 其他运行时错误

### `bp_algorithm`

- **耗时**: 51.75s
- **错误类型**: RuntimeError
- **详情**: `train_dataloader = DataLoader(
^^^^^^^^^^^
File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/torch/utils/data/dataloader.py", line 281, in __init__
raise ValueError(
ValueError: prefetch_factor option could only be specified in multiprocessing.let num_workers > 0 t`
- **stdout (末 5 行)**:
```
(无)
```
- **stderr (末 5 行)**:
```
    train_dataloader = DataLoader(
                       ^^^^^^^^^^^
  File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/torch/utils/data/dataloader.py", line 281, in __init__
    raise ValueError(
ValueError: prefetch_factor option could only be specified in multiprocessing.let num_workers > 0 to enable multiprocessing, otherwise set prefetch_factor to None.
```

### `concat_data`

- **耗时**: 23.46s
- **错误类型**: RuntimeError
- **详情**: `File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/pandas/core/generic.py", line 2312, in to_excel
formatter.write(
File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/pandas/io/formats/excel.py", line 951, in write
raise ValueError(`
- **stdout (末 5 行)**:
```
(无)
```
- **stderr (末 5 行)**:
```
  File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/pandas/core/generic.py", line 2312, in to_excel
    formatter.write(
  File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/pandas/io/formats/excel.py", line 951, in write
    raise ValueError(
ValueError: This sheet is too large! Your sheet size is: 1733000, 7 Max sheet size is: 1048576, 16384
```

### `logic_regresssion`

- **耗时**: 35.82s
- **错误类型**: RuntimeError
- **详情**: `^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/sklearn/linear_model/_logistic.py", line 1208, in fit
raise ValueError(
ValueError: The 'liblinear' solver does not support multiclass classification (n_classes >= 3). Either u`
- **stdout (末 5 行)**:
```
Fitting 5 folds for each of 40 candidates, totalling 200 fits
```
- **stderr (末 5 行)**:
```
    return fit_method(estimator, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/site-packages/sklearn/linear_model/_logistic.py", line 1208, in fit
    raise ValueError(
ValueError: The 'liblinear' solver does not support multiclass classification (n_classes >= 3). Either use another solver or wrap the estimator in a OneVsRestClassifier to keep applying a one-versus-rest scheme.
```

### `lstm_classify`

- **耗时**: 52.96s
- **错误类型**: RuntimeError
- **详情**: `Traceback (most recent call last):
File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code/lstm_classify.py", line 68, in <module>
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many dimensions 'Se`
- **stdout (末 5 行)**:
```
(无)
```
- **stderr (末 5 行)**:
```
Traceback (most recent call last):
  File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code/lstm_classify.py", line 68, in <module>
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many dimensions 'Series'
```

### `rnn_classfiy`

- **耗时**: 52.12s
- **错误类型**: RuntimeError
- **详情**: `Traceback (most recent call last):
File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code/rnn_classfiy.py", line 70, in <module>
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many dimensions 'Ser`
- **stdout (末 5 行)**:
```
(无)
```
- **stderr (末 5 行)**:
```
Traceback (most recent call last):
  File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code/rnn_classfiy.py", line 70, in <module>
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many dimensions 'Series'
```

### `transformer_classify`

- **耗时**: 54.57s
- **错误类型**: RuntimeError
- **详情**: `Traceback (most recent call last):
File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code/transformer_classify.py", line 74, in <module>
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many dimensi`
- **stdout (末 5 行)**:
```
(无)
```
- **stderr (末 5 行)**:
```
Traceback (most recent call last):
  File "/Users/zero/Desktop/master_study/graduation_transfer/sleep_posture/sleep_classify/code/transformer_classify.py", line 74, in <module>
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many dimensions 'Series'
```


---
## 📋 未运行脚本说明

以下 31 个脚本因包含硬编码的 Windows 绝对路径（`F:/...` 或 `E:/...`），
在 macOS 上必然 FileNotFoundError，不再逐一执行。
详见体检报告中的分类：

| 分组 | 脚本数 | 典型路径 |
|---|---|---|
| IMU_sleep_stage (data_deal_code/) | 4 | `F:/master_paper_and_project/IMU_sleep_stage/base_data/...` |
| IMU_sleep_stage (model/) | 7 | `E:/ysl/IMU_sleep_stage/base_data/...` |
| Sleep-pdf (data_deal/) | 5 | `E:/master_paper_and_project/research/...` |
| Sleep-pdf (model/) | 7 | `F:/master_paper_and_project/research/new_project/...` |
| 迁移标签 (code/) | 5 | `E:/master_paper_and_project/sleep_stage/...` |
| 迁移标签 (model/) | 1 | `E:/master_paper_and_project/research/...` |
| Sleep-pdf (origin_data/) | 1 | `serial_port_extract` 已单独运行 |
| feature_deal | 1 | 全注释文档伪装 .py |

---
## 🧠 根因分析与推荐方案

### 1. 有效运行的脚本（5 个）

| 脚本 | 实验结论 |
|---|---|
| `descison_tree` | ✅ AUC: (0.993, 0.994, 0.992) — 决策树分类效果优秀 |
| `kmeans_algorithm` | ✅ Adjusted Rand Index: 0.096 — 无监督聚类效果一般（数据本身有标签） |
| `bar_chart` | ✅ 生成了模型性能对比条形图。RNN-LSTM 综合最优：Acc=98.64%, F1=98.63% |
| `test_psg_data` | ✅ 成功读取 PSG.edf（256Hz, 19通道），提取 ECG 通道数据 |
| `new__hybird_imag` | ✅ 生成混淆矩阵热力图 `confusion_matrix_bold.png` |

### 2. 无实质执行的脚本（3 个）

这些脚本 import 成功、exit code 0，但没有 `__main__` 或只是模型定义：
- **`model_figure`** — 只定义了 RNN-LSTM 模型结构，无 main 入口
- **`serial_port_extract`** — 无串口硬件，exit 0 但报 "could not open port COM5"
- **`SVM_algorithm`** — ⏱ **120s 超时**。数据读取完成（15 个 xlsx），但在 4 个 SVM 模型训练时超时。非 DL，而是 SVM 网格搜索耗时。加长 timeout 或减少 C/gamma 搜索范围即可。

### 3. 源码 bug——简单修复即可运行（5 个）

#### NameError
- **`kdtree_data`**: `Y = new_df.iloc[:, -1]` 被注释掉（第 40-41 行间），取消注释即修复

#### torch.tensor(Series) → ValueError: too many dimensions
- **`lstm_classify`**, **`rnn_classfiy`**, **`transformer_classify`**: `y_train` 是 pandas Series，`torch.tensor(y_train)` 在 PyTorch 新版本中报错。
  - 修复: `y_train_tensor = torch.tensor(y_train.values, dtype=torch.long)`

#### sklearn solver → multiclass
- **`logic_regresssion`**: `LogisticRegression(solver='liblinear')` 不支持 3 分类。
  - 修复: 改 `solver='lbfgs'` 或 `solver='saga'`，liblinear 只能处理二分类

#### PyTorch DataLoader prefetch_factor
- **`bp_algorithm`**: `DataLoader(..., prefetch_factor=2)` 与 `num_workers=0` 冲突（PyTorch 2.x 新行为）。
  - 修复: 删掉 `prefetch_factor=2` 或设 `num_workers=1`

#### Excel 行数超限
- **`concat_data`**: 拼接后 1,733,000 行，超过 Excel 上限 1,048,576。
  - 修复: `df.to_excel()` 前拆分 sheet，或换成 `.to_csv()`

### 4. FileNotFoundError——数据文件不完整（3 个）

- **`verify_model`**: 需要 `../model/kd_tree.m`（模型目录为空 → 先训练再验证）
- **`origin_test`**: 需要 `d0000087.txt`（IMU 原始 hex 数据文件）
- **`test_all`**: 需要 `d0000003.csv`（同上）

### 5. 31 个硬编码路径脚本（Phase 2）

这些脚本含 `F:/...` / `E:/...` 硬编码 Windows 路径，在 macOS 上必然 FileNotFoundError。
详见体检报告的完整分类表。修复方案：用 `pathlib.Path(__file__).parent` 推导相对路径。

### 6. 唯一缺失模块：imblearn

`smote_label.py` 需要 `imblearn` 做 SMOTE 过采样，且本身也有硬编码路径。属 mixed 类型，等 Phase 2 一起处理。

---
## 附录：Cheatsheet

```bash
# 重新运行分析
rm /Users/zero/Desktop/master_study/docs/superpowers/reports/run_results.json
/Users/zero/Desktop/master_study/master_study_env/bin/python tools/run_analysis.py
```

