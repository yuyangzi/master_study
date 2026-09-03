# 脚本可运行性报告

- 运行时间: 2026-06-06
- 更新: 2026-06-07 — 修复 3 个非路径脚本（kdtree_data/bp_algorithm/smote_label），plan: docs/superpowers/plans/2026-06-07-fix-non-path-script-errors.md
- 范围: graduation_transfer/ 48 个 .py 脚本（49 个真实脚本 - 1 跳过 = 48；额外 1 条 `data_deal/test.py` 在磁盘但不在 SCRIPTS_ALL）
- 数据源: 5 旧 (17:12 run_results.json) + 29 新 (本次) + 14 未跑 + 1 跳过（feature_deal.py）
- 环境: venv (Python 3.11, macOS ARM64, torch 2.12 CPU)

## 汇总

| 状态 | 数量 |
|---|---|
| ✅ 运行成功 | 19 |
| ❌ 失败 | 7 |
| ⏱ 超时 | 8 |
| ⚠️ 跳过 | 1 |（feature_deal.py 全注释）

## 修复优先级

| 优先级 | 数量 | 处理建议 |
|---|---|---|
| 🟢 P0-快 | 0 | 现在修，~5 分钟 |
| 🟡 P1-中 | 17 | 今天修，~30 分钟 |
| 🟠 P2-数据 | 2 | 数据到位后修 |
| 🔵 P3-GPU | 3 | 上服务器跑 |
| ⚪ P4-可忽略 | 26 | 视情况 |

### sleep_classify（11 条）

#### ⏱ `SVM_algorithm.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/SVM_algorithm.py`
- 功能: 向量机进行处理
- Imports: matplotlib, numpy, os, pandas, sklearn
- 运行: exit=-999, 120.0s
- 修复: (手工诊断)
- 优先级: ⚪ P4-可忽略
- 数据源: 旧 (17:12 JSON)


#### ✅ `bp_algorithm.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/bp_algorithm.py`
- 功能: 全连接神经网络进行数据分类
- Imports: numpy, os, pandas, pathlib, sklearn
- 运行: exit=0, 100.5s; 修复 line 134 删除 prefetch_factor=2; 5 epochs Acc=0.987 (已恢复 total_epoch=100)
- 优先级: ⚪ P4-可忽略
- 数据源: 旧 (17:12 JSON) + 2026-06-07 验证


#### ❔ `concat_data.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/util/concat_data.py`
- 功能: 主要将所有的孕妇的数据合并为一个xlsx的文件
- Imports: os, pandas, tqdm
- 优先级: 🟡 P1-中


#### ✅ `descison_tree.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/descison_tree.py`
- 功能: 使用决策树对睡眠数据进行分类
- Imports: matplotlib, numpy, os, pandas, sklearn
- 运行: exit=0, 108.9s
- 优先级: ⚪ P4-可忽略
- 数据源: 旧 (17:12 JSON)


#### ✅ `kdtree_data.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/kdtree_data.py`
- 功能: (无法推断)
- Imports: numpy, os, pandas, sklearn, tqdm
- 运行: exit=0, 99.7s; 修复 line 40 取消 Y 注释; Acc=1.00
- 优先级: ⚪ P4-可忽略
- 数据源: 旧 (17:12 JSON) + 2026-06-07 验证


#### ✅ `kmeans_algorithm.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/kmeans_algorithm.py`
- 功能: 聚类的相关问题的处理
- Imports: numpy, os, pandas, sklearn, tqdm
- 运行: exit=0, 103.5s
- 优先级: ⚪ P4-可忽略
- 数据源: 旧 (17:12 JSON)


#### ❔ `logic_regresssion.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/logic_regresssion.py`
- 功能: (无法推断)
- Imports: matplotlib, numpy, os, pandas, sklearn
- 优先级: ⚪ P4-可忽略


#### ❔ `lstm_classify.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/lstm_classify.py`
- 功能: (无法推断)
- Imports: numpy, os, pandas, sklearn, torch
- 优先级: ⚪ P4-可忽略


#### ❔ `rnn_classfiy.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/rnn_classfiy.py`
- 功能: (无法推断)
- Imports: numpy, os, pandas, sklearn, torch
- 优先级: ⚪ P4-可忽略


#### ❔ `transformer_classify.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/transformer_classify.py`
- 功能: (无法推断)
- Imports: numpy, os, pandas, sklearn, torch
- 优先级: ⚪ P4-可忽略


#### ❔ `verify_model.py`

- 路径: `graduation_transfer/sleep_posture/sleep_classify/code/verify_model.py`
- 功能: 主要是为了进行数据验证
- Imports: joblib, numpy, pandas
- 优先级: ⚪ P4-可忽略


### IMU（11 条）

#### ✅ `cal_label_count.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/cal_label_count.py`
- 功能: 统计/计数脚本
- Imports: os, pandas, pathlib, sys, typing
- 运行: exit=0, 1.5s
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ✅ `data_deal.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/data_deal.py`
- 功能: 数据预处理脚本（datetime, numpy, os）
- Imports: datetime, numpy, os, pandas, pathlib
- 运行: exit=0, 3.1s
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ⏱ `imu_cnn.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_cnn.py`
- 功能: 用于使用CNN对睡眠阶段的训练的处理
- Imports: pandas, pathlib, sklearn, torch
- 运行: exit=-999, 300.0s
- 修复: (手工诊断)
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ⏱ `imu_cnn_lstm.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_cnn_lstm.py`
- 功能: 用于使用CNN+LSTM混合模型对睡眠阶段的训练处理
- Imports: pandas, pathlib, sklearn, torch
- 运行: exit=-999, 300.0s
- 修复: (手工诊断)
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ⏱ `imu_cnn_rnn.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_cnn_rnn.py`
- 功能: 用于使用CNN+RNN混合模型对睡眠阶段的训练处理
- Imports: pandas, pathlib, sklearn, torch
- 运行: exit=-999, 300.0s
- 修复: (手工诊断)
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ✅ `imu_kdtree.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_kdtree.py`
- 功能: 使用knn的算法进行PSG的睡眠阶段的预测
- Imports: pandas, pathlib, sklearn
- 运行: exit=0, 38.2s
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ⏱ `imu_lstm.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_lstm.py`
- 功能: (无法推断)
- Imports: matplotlib, numpy, pandas, pathlib, sklearn
- 运行: exit=-999, 300.0s
- 修复: (手工诊断)
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ⏱ `imu_lstm_rnn.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_lstm_rnn.py`
- 功能: 使用RNN和LSTM进行训练
- Imports: numpy, pandas, pathlib, sklearn, torch
- 运行: exit=-999, 300.0s
- 修复: (手工诊断)
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ⏱ `imu_rnn.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_rnn.py`
- 功能: (无法推断)
- Imports: matplotlib, numpy, pandas, pathlib, sklearn
- 运行: exit=-999, 300.0s
- 修复: (手工诊断)
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ❌ `smote_label.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/smote_label.py`
- 功能: (无法推断)
- Imports: imblearn, os, pandas, pathlib
- 运行: exit=1, ~80s
- 错误: `ValueError: With over-sampling methods, the number of samples in a class should be greater or equal to the original number of samples. Originally, there is 1351647 samples and 100000 samples are asked.`
- 修复: 部分修复：defensive import（line 5-10 + 27-30）; 数据逻辑 bug 未修（SMOTE 只能过采样，class 0 有 1.35M 样本，目标 100k 需用 RandomUnderSampler）
- 优先级: 🟡 P1-中
- 数据源: 新 (本次) + 2026-06-07 部分修复


#### ⏱ `train_data_deal.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/train_data_deal.py`
- 功能: 训练机器学习模型（collections, numpy, os）
- Imports: collections, numpy, os, pandas, pathlib
- 运行: exit=-999, 120.0s
- 修复: (手工诊断)
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


### 迁移（8 条）

#### ✅ `add_imu_label_4.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/add_imu_label_4.py`
- 功能: (无法推断)
- Imports: pandas, pathlib
- 运行: exit=0, 3.5s
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ❌ `eeg_data_add_label_3.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/eeg_data_add_label_3.py`
- 功能: 将对应的睡眠数据增加对应的
- Imports: numpy, pandas, pathlib, sklearn, torch
- 运行: exit=1, 2.4s
- 错误: `FileNotFoundError: FileNotFoundError: [Errno 2] No such file or directory: '../model/rnn_lstm/best_model_epoch32.pth'`
- 行号: 67
- 修复: 数据文件不存在。修复：检查路径或补充数据
- 优先级: 🔵 P3-GPU
- 数据源: 新 (本次)


#### ❌ `eeg_data_deal_1.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/eeg_data_deal_1.py`
- 功能: 数据预处理脚本（numpy, pandas, pathlib）
- Imports: numpy, pandas, pathlib
- 运行: exit=1, 0.3s
- 错误: `FileNotFoundError: FileNotFoundError: [Errno 2] No such file or directory: '/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/rawdata/gjxeeg_gjx_0715.xls'`
- 行号: 61
- 修复: 数据文件不存在。修复：检查路径或补充数据
- 优先级: 🟠 P2-数据
- 数据源: 新 (本次)


#### ❌ `eeg_data_to_base_2.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/eeg_data_to_base_2.py`
- 功能: 此处将对应的eeg的data转化为对应的可以训练的数据
- Imports: datetime, matplotlib, numpy, pandas, pathlib
- 运行: exit=1, 2.5s
- 错误: `FileNotFoundError: FileNotFoundError: [Errno 2] No such file or directory: '/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/EEG_data/gjxpsg_eeg_gjx_0715.csv'`
- 行号: 177
- 修复: IMU 原始数据缺失。修复：把被试数据放到 data/ 目录，或检查 Path(__file__) 推导是否正确
- 优先级: 🔵 P3-GPU
- 数据源: 新 (本次)


#### ❌ `imu_data_deal_1.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/imu_data_deal_1.py`
- 功能: 用于处理imu的数据
- Imports: numpy, pandas, pathlib
- 运行: exit=1, 0.3s
- 错误: `FileNotFoundError: FileNotFoundError: [Errno 2] No such file or directory: '/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/rawdata/gjximu_gjx_0715.xls'`
- 行号: 34
- 修复: 数据文件不存在。修复：检查路径或补充数据
- 优先级: 🟠 P2-数据
- 数据源: 新 (本次)


#### ❌ `integrate_deal_process-只看这个代码.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/integrate_deal_process-只看这个代码.py`
- 功能: 整合所有的数据的处理流程
- Imports: numpy, pandas, pathlib, scipy, sklearn
- 运行: exit=1, 2.0s
- 错误: `FileNotFoundError: FileNotFoundError: [Errno 2] No such file or directory: '/Users/zero/Desktop/master_study/graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/EEG_data/complete_pathliu/eeg_liu.xls'`
- 行号: 396
- 修复: 数据文件不存在。修复：检查路径或补充数据
- 优先级: 🔵 P3-GPU
- 数据源: 新 (本次)


#### ✅ `psg_rnn_lstm.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/model/psg_rnn_lstm.py`
- 功能: 使用RNN和LSTM进行训练
- Imports: numpy, pandas, pathlib, sklearn, torch
- 运行: exit=0, 98.0s
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ❔ `test_all.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/test_all.py`
- 功能: 测试/验证脚本
- Imports: matplotlib
- 优先级: 🟡 P1-中


### Sleep-pdf/data（5 条）

#### ✅ `balance_data-提取后数据的预处理.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/balance_data-提取后数据的预处理.py`
- 功能: (无法推断)
- Imports: os, pandas, pathlib
- 运行: exit=0, 0.7s
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ❌ `new_feature_deal-EEG提取.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/new_feature_deal-EEG提取.py`
- 功能: 数据预处理脚本（datetime, mne, numpy）
- Imports: datetime, mne, numpy, os, pandas
- 运行: exit=1, 1.2s
- 错误: `RuntimeError: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/Users/zero/Desktop/master_study/master_study_env/lib/python3.11/random.py", line 456, in sample
raise ValueError("Sample larger than popula`
- 行号: 159
- 修复: (手工诊断)
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ✅ `raw_data_extract.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/raw_data_extract.py`
- 功能: 用于睡眠脑电波原始数据的提取
- Imports: datetime, numpy, os, pandas, pathlib
- 运行: exit=0, 1.2s
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ❔ `test.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/test.py`
- 功能: 测试/验证脚本
- Imports: mne, numpy, pandas, pathlib, scipy
- 优先级: 🟡 P1-中


#### ❔ `test_psg_data.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/test_psg_data.py`
- 功能: 测试/验证脚本
- Imports: mne
- 优先级: 🟡 P1-中


### Sleep-pdf/model（11 条）

#### ❔ `bar_chart.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/bar_chart.py`
- 功能: 用于生成各模型性能指标的条形图，用于SCI论文
- Imports: matplotlib, numpy, os, seaborn
- 优先级: ⚪ P4-可忽略


#### ✅ `basic_rnn.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/basic_rnn.py`
- 功能: (无法推断)
- Imports: matplotlib, numpy, pandas, pathlib, sklearn
- 运行: exit=0, 40.8s
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ✅ `decsion_tree.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/decsion_tree.py`
- 功能: 使用knn的算法进行PSG的睡眠阶段的预测
- Imports: pandas, pathlib, sklearn
- 运行: exit=0, 1.7s
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ✅ `hybird_matrix.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/hybird_matrix.py`
- 功能: 用于生成混淆矩阵，用于SCI论文中的图
- Imports: matplotlib, numpy, os, pandas, pathlib
- 运行: exit=0, 104.6s
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ❔ `model_figure.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/model_figure.py`
- 功能: 生成可视化图表/混淆矩阵
- Imports: numpy, pandas, sklearn, torch, torchviz
- 优先级: ⚪ P4-可忽略


#### ❔ `new__hybird_imag.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/new__hybird_imag.py`
- 功能: 生成可视化图表/混淆矩阵
- Imports: matplotlib, pandas, seaborn
- 优先级: ⚪ P4-可忽略


#### ✅ `psg_cnn.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_cnn.py`
- 功能: 用于使用CNN对睡眠阶段的训练的处理
- Imports: numpy, pandas, pathlib, sklearn, torch
- 运行: exit=0, 86.3s
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ✅ `psg_kdtree.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_kdtree.py`
- 功能: 使用knn的算法进行PSG的睡眠阶段的预测
- Imports: pandas, pathlib, sklearn
- 运行: exit=0, 1.5s
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ✅ `psg_knn.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_knn.py`
- 功能: 使用knn的算法进行PSG的睡眠阶段的预测
- Imports: pandas, pathlib, sklearn
- 运行: exit=0, 1.5s
- 优先级: 🟡 P1-中
- 数据源: 新 (本次)


#### ✅ `psg_lstm.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_lstm.py`
- 功能: (无法推断)
- Imports: matplotlib, numpy, pandas, pathlib, sklearn
- 运行: exit=0, 55.2s
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


#### ✅ `psg_rnn_lstm.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_rnn_lstm.py`
- 功能: 使用RNN和LSTM进行训练
- Imports: numpy, pandas, pathlib, sklearn, torch
- 运行: exit=0, 112.7s
- 优先级: ⚪ P4-可忽略
- 数据源: 新 (本次)


### Sleep-pdf/origin（2 条）

#### ❔ `serial_port_extract.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/serial_port_extract.py`
- 功能: 数据提取脚本（json, serial, time）
- Imports: json, serial, time
- 优先级: 🟡 P1-中


#### ❔ `test.py`

- 路径: `graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/test.py`
- 功能: 测试/验证脚本
- Imports: matplotlib
- 优先级: 🟡 P1-中


### 跳过的脚本

- `feature_deal.py` — 全注释伪 .py，136 行全部注释

## 附录

- 跑 29 个脚本: `tools/run_analysis.py --filter sleep_stage`
- 重新生成报告: `tools/generate_runnability_report.py`
- 2026-06-07 plan 修复 3 条：kdtree_data/bp_algorithm/smote_label（commit 7c45397）
- 旧 run_results.json: 17:12 5 条 sleep_classify 验证
- 旧 run-analysis-report.md: 15:29 18 个完整分析（markdown，无法结构化合并）
