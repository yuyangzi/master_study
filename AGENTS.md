# AGENTS.md — 研究生睡眠研究项目工作区

**生成日期:** 2026-06-06
**分支:** main

## 项目性质

研究生课题工作区。**不是标准软件项目** — 没有测试框架、CI/CD、linter、pyproject.toml。验证靠跑训练脚本看 `Test Accuracy:` 输出。

## 目录结构

```
master_study/
├── graduation_transfer/          # 课题代码与数据
│   ├── sleep_posture/sleep_classify/   # 睡姿分类（自有 git 仓库）
│   └── sleep_stage/.../SleepEDF数据处理/ # 睡眠分期（3 子工程，不在 git 下）
├── tools/                        # 工具脚本（4 个）
├── docs/superpowers/             # 分析报告/计划/设计文档
├── util/                         # 工具（concat_data.py）
└── venv/                         # 本地 conda（空壳，只含 pip/setuptools）
```

## 关键陷阱

| 陷阱 | 说明 | 位置 |
|------|------|------|
| Windows 硬编码路径 | 20+ 文件含 `F:/...` 路径，macOS 失效 | `sleep_stage/` 下几乎所有 `.py` |
| 环境缺失依赖 | 本地 venv 无 torch/sklearn/pandas | 训练需远程服务器或 PyCharm |
| 嵌套 git 仓库 | `sleep_classify/` 自有 `.git`（分支 `release.new`），工作区不干净 | 改代码前先 `git status` |
| 中文文件名/路径 | 含空格、括号、汉字，shell 需引号包裹 | `sleep_stage/` 全目录 |
| 拼写错误文件名 | 不要"修正"：`descison_tree`、`logic_regresssion`、`rnn_classfiy` 等 | 各 `code/` 和 `model/` 目录 |

## 数据布局

### 睡姿分类（posture）
- **原始数据**: `after_process_data/after_process_data/` 下 165 个 `*.xlsx`
- **标签规则**: `left`=0（左侧卧）、`m`=1（仰卧）、`right`=2（右侧卧）；`*_motion.xlsx` 不参与训练
- **特征**: 6 列 IMU 特征 `feature1-feature6`（3 加速度 + 3 角速度）
- **训练脚本**: `code/` 下 9 个独立入口，无统一 `train.py`
- **⚠️ 标签约定不一致**: `kdtree_data.py` 使用 `{1: left, 2: m, 3: right}`，其他脚本使用 `{0: left, 1: m, 2: right}`（与 AGENTS.md 一致）。这是历史遗留问题，暂不修复。

### 睡眠分期（sleep stage）- 3 子工程
- **IMU 标签**: `base_data/` 含 `train_label.csv`、`liu_imu_label.csv` 等
- **标签迁移**: `integrate_deal_process-只看这个代码.py` 为整合入口
- **Sleep-pdf**: `new_project/` 最新工程，含 `psg_*.py` 模型 + `merge_data/` CSV
- **被试**: chy、gjx、liu 三人，每人有对应 EEG + IMU 原始 `.xls` 文件

## 约定

- **中文注释/docstring** 普遍，类名/变量名英文 — 不要翻译
- **超参数默认值**: epochs=100、batch_size=128、lr=0.001（Adam）、random_state=42、test_size=0.2
- **入口**: `if __name__ == "__main__"` 为主；`bp_algorithm.py` 特殊用 `t0()`
- **运行目录**: 每个脚本从自身所在目录执行（依赖 `../xxx` 相对路径）

## 反模式（此项目特有）

- **`except: pass`** — 15+ 文件有空 except 块，静默吞掉数据加载错误
- **绝对 Windows 路径** — 20+ 文件硬编码 `F:/master_paper_and_project/...`，不可移植
- **依赖缺失** — 本地 venv 无 ML 包，import torch/sklearn/pandas 会 ImportError
- **git 外关键文件** — `sleep_stage/` 全目录不受 git 管理，需手动备份

## 命令

```bash
# 睡姿训练（从 code/ 目录执行）
cd graduation_transfer/sleep_posture/sleep_classify/code
../../../../venv/bin/python bp_algorithm.py

# 运行分析工具
venv/bin/python tools/run_analysis.py

# 健康检查
venv/bin/python tools/script_health_check.py
```

## 远程工作流

训练在 `root@159.75.177.109:22` 或 PyCharm `Python 3.7 (pytorch)` 环境执行。本地只做编辑和小规模验证。
