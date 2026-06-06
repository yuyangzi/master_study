# AGENTS.md — 研究生睡眠研究项目工作区

## 仓库性质

这是研究生课题工作区，不是常规软件项目。**没有测试框架、没有 CI、没有 linter、没有 requirements/pyproject**。`util/save_execl.xlsx`（17 MB）是 `concat_data.py` 的生成产物，不应提交到 git。

## 顶层结构

工作区根：`/Users/zero/Desktop/master_study`

- `master_study_env/` — 本地 conda 环境（Python 3.11），但**只装了 `packaging/pip/setuptools/wheel`**，并未安装 `torch/sklearn/pandas`。真正的训练用环境是 PyCharm 里的 `Python 3.7 (pytorch)`，或在远程服务器 `root@159.75.177.109:22`（见 `.idea/deployment.xml`）。
- `graduation_transfer/` — 课题代码与数据：
  - `sleep_posture/sleep_classify/` — **唯一被 git 跟踪的子项目**（远程：`git@github.com:yeshangle/sleep_classify.git`，当前分支 `release.new`）。
  - `sleep_stage/睡眠研究/SleepEDF数据处理/` — 睡眠分期相关三个子工程（IMU 带标签 / 迁移标签 / Sleep-pdf），**全部不在 git 控制下**。

## git 状态（重要！）

`cd graduation_transfer/sleep_posture/sleep_classify` 后：
- 当前分支是 `release.new`，本地相对 origin 已显示有未提交改动（`code/*.py` 被修改、`README.md` 与 `myplot.png` 被删除、`.idea/` 未跟踪）。
- 不要在没有用户明确要求的情况下 `git add/commit/push`，更不要 `git checkout .` / `git reset` 把已删除的 `README.md` 救回来——这些可能是有意为之的整理。

## 跨平台路径陷阱（最高频踩坑点）

几乎所有 `sleep_stage/...` 子项目的 Python 文件里都硬编码了 Windows 风格路径，例如：

- `F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv`
- `F:/master_paper_and_project/IMU_sleep_stage/base_data/train_label.csv`
- `F:/ysl/IMU_sleep_stage/base_data/train_label.csv`
- `F:\master_paper_and_project\IMU_sleep_stage\base_data\liu_imu_label.csv`

在当前 macOS 工作区这些路径**全部失效**。如果用户让你跑 `sleep_stage/` 下的脚本，必须先把这些 `F:/...` 替换成 macOS 上对应的相对/绝对路径（建议改为脚本所在目录的相对路径，或 `pathlib.Path(__file__).parent` 推导）。

`sleep_posture/sleep_classify/code/` 下的脚本用的是相对路径（`../after_process_data/...`、`../model/...`），从 `code/` 目录运行就 OK，**不要在仓库根目录直接 `python code/bp_algorithm.py`**。

## 数据布局速查

### 睡姿（posture）

- 原始数据：`graduation_transfer/sleep_posture/sleep_classify/after_process_data/after_process_data/` 下 165 个 `*.xlsx`。文件名约定决定标签：以 `left.xlsx` → 0（左侧卧）、`m.xlsx` → 1（仰卧）、`right.xlsx` → 2（右侧卧）；`*_motion.xlsx` 是运动段、不参与训练。
- 合并产物：`util/save_execl.xlsx`（由 `util/concat_data.py` 生成）。
- 模型产物：`model/` 目录（`verify_model.py` 期望 `kd_tree.m` 存在；目前是空目录）。
- 训练脚本：`code/{bp_algorithm, descison_tree, kdtree_data, kmeans_algorithm, logic_regresssion, lstm_classify, rnn_classfiy, SVM_algorithm, transformer_classify}.py` — **每个文件都是独立入口**，没有统一的 `train.py`。

### 睡眠分期（sleep stage）

- `IMU_sleep_stage-带有标签的IMU代码处理/`：标签处理 + 模型训练。`base_data/{liu_imu_label, reasonable_label, train_label, label_count}.csv`；`data_deal_code/` 里有 `data_deal.py`（原始数据 → CSV）、`smote_label.py`（SMOTE 过采样）、`cal_label_count.py`、`train_data_deal.py`。`model/` 里有 `imu_{cnn,cnn_lstm,cnn_rnn,kdtree,lstm,lstm_rnn,rnn}.py`。
- `sleep_stage-迁移标签代码/`：EEG ↔ IMU 标签迁移。`code-数据处理的代码(最终给IMU打上标签)/integrate_deal_process-只看这个代码.py` 文件名提示这是**最终整合入口**。数据目录有 `rawdata/`（按 `chy/gjx/liu` 等被试分目录）、`EEG_data/`、`PSG_deal_data/`、`IMU_deal_data/`、`imu_eeg实验数据/`、`time_frequent_signal/`。
- `Sleep-pdf处理代码/new_project/`：最新工程。`model-模型训练代码/` 里有 `psg_{cnn,kdtree,knn,lstm,rnn_lstm}.py`、`basic_rnn.py`、`decsion_tree.py`、`hybird_matrix.py` 等。

## 约定与风格

- **中文注释 / 中文 docstring** 普遍；类名、变量名却是英文。不要把中文注释翻译成英文。
- 文件名/目录名**中英文混用且含空格、括号、`-` 分隔符**，例如 `code-数据处理的代码(最终给IMU打上标签)/`、`data_deal-sleep-pdf原始数据处理/`。shell 引用必须加引号。
- 文件名有拼写错误（沿用即可，不要"修正"）：`descison_tree.py`（→ decision）、`logic_regresssion.py`（→ regression）、`rnn_classfiy.py`（→ classify）、`decsion_tree.py`（→ decision）、`hybird_matrix.py`（→ hybrid）。
- 各脚本以 `if __name__ == "__main__":` 启动；`bp_algorithm.py` 入口是 `t0()`，调用 `python code/bp_algorithm.py` 即可训练。
- 默认 `epochs=100`、`batch_size=128`、`lr=0.001`（Adam）、`random_state=42`、训练/测试划分 `test_size=0.2`。
- 特征列名硬编码为 `['feature1',..., 'feature6']`（IMU 6 轴：3 加速度 + 3 角速度），不要擅自改名。

## 验证与测试

- **没有任何单元测试或集成测试**。"验证"靠直接跑训练脚本看 `Test Accuracy:` 输出，或用 `code/verify_model.py` 加载训练好的模型预测几条手写样本。
- 训练很慢（100 epoch、165 文件全量读入）。改算法时先在小数据/小 epoch 上确认能跑通，再放大。
- 没有 lint/typecheck 命令，不要假想 `ruff`/`mypy`/`pytest` 在这里能用。

## 远程工作流

`.idea/deployment.xml` 显示代码会部署到 `root@159.75.177.109:22`，且 PyCharm SDK 是 `Python 3.7 (pytorch)`。如果用户提到"服务器/远程/159.75.177.109"，说明训练是在那台机器上做的；本地只做编辑和小规模验证。

## 经验法则

- 进入 `sleep_classify/` 改代码前先 `git status` 看一眼，工作区不干净。
- 跑 `sleep_stage/` 下的脚本前先全文 grep `F:/` / `F:\` 并替换路径。
- 不要在仓库根目录跑 `python`；每个脚本的"运行目录"就是它自己所在目录（依赖 `../xxx` 相对路径）。
- 不要主动 `git add` `util/save_execl.xlsx`、`after_process_data/`、`rawdata/`、`EEG_data/`、`PSG_deal_data/` 等大文件/数据目录。
