## 睡眠分期研究（SleepEDF数据处理）

使用EEG+IMU数据进行睡眠分期分类，含3个子工程。

1. IMU_sleep_stage-带有标签的IMU代码处理/：纯IMU模型（imu_cnn.py等），数据在base_data/*.csv，代码在data_deal_code/。
2. sleep_stage-迁移标签代码/：EEG标签迁移到IMU，主入口：code-数据处理的代码(最终给IMU打上标签)/integrate_deal_process-只看这个代码.py，被试：chy/gjx/liu，原始数据为.xls。
3. Sleep-pdf处理代码/new_project/：最新工程，模型为psg_*.py，合并数据在merge_data/*.csv。

⚠️ 未被git管理，所有代码和数据必须手动备份。

⚠️ 20+文件硬编码F:/...路径，运行前必须执行tools/fix_paths.py或使用pathlib适配macOS。

⚠️ 每个脚本必须在其自身目录下运行，本地venv无torch/sklearn/pandas，需在远程服务器或PyCharm中执行。

模型检查点位于model/rnn_lstm/（26个）和model/new_model.pth等。

反模式：多数脚本含except:pass，静默吞错误；中文路径含空格，shell中必须用引号包裹。