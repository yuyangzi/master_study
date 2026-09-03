# Python 脚本可运行性体检报告

- 体检时间: 2026-06-06
- 体检范围: 51 个 Python 脚本
- 体检深度: 静态检查 + 导入可行性 (未执行 main，未执行模块代码)
- 体检环境: master_study_env (只含 packaging/pip/setuptools/wheel)
- 工具脚本: tools/script_health_check.py

## 汇总：环境 vs 脚本本身

| 维度 | 数量 |
|------|------|
| 脚本总数 | 51 |
| 语法 OK | 51 |
| 语法失败 | 0 |
| 脚本本身有问题 (语法/硬编码路径) | 31 |
| 只缺包、脚本本身健康 (env-only) | 0 |
| 完全 clean | 20 |


## 缺失最多的模块 (Top 10)

- `imblearn` — 1 个脚本依赖，env 内 MISSING → `pip install imblearn`


## 优先级建议（基于修复工作量）

1. **易修复（仅装包）**: 装上缺失的包就能跑，列在 "env-only" 分组
2. **中等（装包 + 改路径）**: 还要把 F:/... 改成 __file__ 相对路径
3. **难（脚本本身有语法/逻辑问题）**: 需要人工 review


## 按子项目分节详述（每个脚本一节）
### sleep_classify/
#### ✅ SVM_algorithm.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: matplotlib, numpy, os, pandas, sklearn, sys, time, tqdm, warnings
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ bp_algorithm.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: numpy, os, pandas, pathlib, sklearn, sys, torch, tqdm
- 缺失: (无)
- 跳过 main: 是
- 建议: 无需修改

#### ✅ descison_tree.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: matplotlib, numpy, os, pandas, sklearn, sys, tqdm, warnings
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ kdtree_data.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: numpy, os, pandas, sklearn, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ kmeans_algorithm.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: numpy, os, pandas, sklearn, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ logic_regresssion.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: matplotlib, numpy, os, pandas, sklearn, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ lstm_classify.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: numpy, os, pandas, sklearn, torch, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ rnn_classfiy.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: numpy, os, pandas, sklearn, torch, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ transformer_classify.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: numpy, os, pandas, sklearn, torch, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ verify_model.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: joblib, numpy, pandas
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ concat_data.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: os, pandas, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

### sleep_stage/IMU_sleep_stage/
#### ❌ cal_label_count.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/IMU_sleep_stage/base_data/train_label.csv, F:/master_paper_and_project/IMU_sleep_stage/base_data/label_count.csv
- 全注释: 否
- Imports: os, pandas, sys, typing
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ data_deal.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:\master_paper_and_project\IMU_sleep_stage\base_data\liu_imu_label.csv, F:\master_paper_and_project\IMU_sleep_stage\deal_data_csv
- 全注释: 否
- Imports: datetime, numpy, os, pandas, pathlib, random
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ smote_label.py  (issue_type: mixed)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/IMU_sleep_stage/base_data/liu_imu_label.csv, F:/master_paper_and_project/IMU_sleep_stage/base_data/liu_imu_label_smote_label0_100k.csv
- 全注释: 否
- Imports: imblearn, os, pandas
- 缺失: imblearn (MISSING)
- 跳过 main: 是
- 建议: `pip install imblearn`；把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ train_data_deal.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/IMU_sleep_stage/base_data/reasonable_label.csv, F:/master_paper_and_project/IMU_sleep_stage/base_data/train_label.csv
- 全注释: 否
- Imports: collections, numpy, os, pandas, sys
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ imu_cnn.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/ysl/IMU_sleep_stage/base_data/train_label.csv
- 全注释: 否
- Imports: pandas, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ imu_cnn_lstm.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/ysl/IMU_sleep_stage/base_data/train_label.csv
- 全注释: 否
- Imports: pandas, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ imu_cnn_rnn.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/ysl/IMU_sleep_stage/base_data/train_label.csv
- 全注释: 否
- Imports: pandas, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ imu_kdtree.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/IMU_sleep_stage/base_data/train_label.csv
- 全注释: 否
- Imports: pandas, sklearn
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ imu_lstm.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/ysl/IMU_sleep_stage/base_data/train_label.csv
- 全注释: 否
- Imports: matplotlib, numpy, pandas, sklearn, torch, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ imu_lstm_rnn.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/ysl/IMU_sleep_stage/base_data/train_label.csv
- 全注释: 否
- Imports: numpy, pandas, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ imu_rnn.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/ysl/IMU_sleep_stage/base_data/train_label.csv
- 全注释: 否
- Imports: matplotlib, numpy, pandas, sklearn, torch, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

### sleep_stage/Sleep-pdf/
#### ❌ balance_data-提取后数据的预处理.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:\master_paper_and_project\research\new_project\merge_data\2025_09_15_21_data.csv, E:\master_paper_and_project\research\new_project\merge_data
- 全注释: 否
- Imports: os, pandas, pathlib
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ⚠️ feature_deal.py  (issue_type: all-commented)
- 语法: OK
- 硬编码路径: r_path = "E:/master_paper_and_project/research/all_data/sleep-cassette/", e_path = "E:/master_paper_and_project/research/new_project/merge_data/" +
- 全注释: 是
- Imports: (空)
- 缺失: (无)
- 跳过 main: 否
- 建议: 该文件是文档伪装的 .py。如不需要可删除；如需保留请改成 `.md` 或启用代码

#### ❌ new_feature_deal-EEG提取.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/research/all_data/sleep-cassette/, E:/master_paper_and_project/research/new_project/merge_data/
- 全注释: 否
- Imports: datetime, mne, numpy, os, pandas, random, scipy
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ raw_data_extract.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/research/new_project/raw_data/ecg_chy1.xls
- 全注释: 否
- Imports: datetime, numpy, os, pandas, random, scipy
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ test.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/research/all_data/sleep-cassette/SC4001E0-PSG.edf, E:/master_paper_and_project/research/all_data/sleep-cassette/SC4001EC-Hypnogram.edf, E:/master_paper_and_project/research/all_data/sleep-cassette/SC4001E0-PSG.edf, E:/master_paper_and_project/research/all_data/sleep-cassette/SC4001EC-Hypnogram.edf
- 全注释: 否
- Imports: mne, numpy, pandas, scipy
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ✅ test_psg_data.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: mne
- 缺失: (无)
- 跳过 main: 是
- 建议: 无需修改

#### ✅ bar_chart.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: matplotlib, numpy, os, seaborn
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ❌ basic_rnn.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv
- 全注释: 否
- Imports: matplotlib, numpy, pandas, sklearn, torch, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ decsion_tree.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv
- 全注释: 否
- Imports: pandas, sklearn
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ hybird_matrix.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv
- 全注释: 否
- Imports: matplotlib, numpy, os, pandas, seaborn, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ✅ model_figure.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: numpy, pandas, sklearn, torch, torchviz
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ new__hybird_imag.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: matplotlib, pandas, seaborn
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ❌ psg_cnn.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv
- 全注释: 否
- Imports: numpy, pandas, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ psg_kdtree.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/research/new_project/merge_data/2025_01_14_16_data.csv
- 全注释: 否
- Imports: pandas, sklearn
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ psg_knn.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv
- 全注释: 否
- Imports: pandas, sklearn
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ psg_lstm.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv
- 全注释: 否
- Imports: matplotlib, numpy, pandas, sklearn, torch, tqdm
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ psg_rnn_lstm.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv
- 全注释: 否
- Imports: numpy, pandas, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ✅ serial_port_extract.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: json, serial, time
- 缺失: (无)
- 跳过 main: 是
- 建议: 无需修改

#### ✅ test.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: matplotlib
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

### __init__/
#### ✅ __init__.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: (空)
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ✅ __init__.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: (空)
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

### sleep_stage/迁移标签/
#### ❌ add_imu_label_4.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/sleep_stage/time_frequent_signal/label_gjx/time_frequent_label_gjx_0715.csv, E:/master_paper_and_project/sleep_stage/EEG_data/imu_gjx/imu_gjx_0715.csv, E:/master_paper_and_project/sleep_stage/time_frequent_signal/imu_label_gjx/imu_label_gjx.csv
- 全注释: 否
- Imports: pandas
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ eeg_data_add_label_3.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/sleep_stage/time_frequent_signal/gjx/, E:/master_paper_and_project/sleep_stage/time_frequent_signal/label_gjx/
- 全注释: 否
- Imports: numpy, pandas, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ eeg_data_deal_1.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/sleep_stage/rawdata/gjx/, E:/master_paper_and_project/sleep_stage/EEG_data/gjx/
- 全注释: 否
- Imports: numpy, pandas
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ eeg_data_to_base_2.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/sleep_stage/EEG_data/gjx/, E:/master_paper_and_project/sleep_stage/time_frequent_signal/gjx/
- 全注释: 否
- Imports: datetime, matplotlib, numpy, pandas, scipy, torch
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ imu_data_deal_1.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/sleep_stage/rawdata/gjx/, E:/master_paper_and_project/sleep_stage/EEG_data/imu_gjx/
- 全注释: 否
- Imports: numpy, pandas
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ❌ integrate_deal_process-只看这个代码.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/master_paper_and_project/sleep_stage/model/rnn_lstm/best_model_epoch36.pth, F:/master_paper_and_project/sleep_stage/PSG_deal_data/deal_data/, F:/master_paper_and_project/sleep_stage/PSG_deal_data/label_data/, F:/master_paper_and_project/sleep_stage/PSG_deal_data/frequent_date_data/, F:/master_paper_and_project/sleep_stage/IMU_deal_data/deal_data/
- 全注释: 否
- Imports: numpy, pandas, scipy, sklearn, torch
- 缺失: (无)
- 跳过 main: 是
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ✅ test_all.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: matplotlib
- 缺失: (无)
- 跳过 main: 是
- 建议: 无需修改

#### ❌ psg_rnn_lstm.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: E:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv
- 全注释: 否
- Imports: numpy, pandas, sklearn, torch
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径
