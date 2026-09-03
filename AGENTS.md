# AGENTS.md — 研究生睡眠研究项目工作区

**更新日期:** 2026-09-03
**分支:** main

## 项目性质

研究生课题工作区。**不是标准软件项目** — 没有测试框架、CI/CD、linter、pyproject.toml。验证靠跑训练脚本看 `Test Accuracy:` 输出。

## 目录结构

```
master_study/
├── graduation_transfer/                  # 课题代码与数据
│   ├── sleep_posture/sleep_classify/     # 睡姿分类（自有 git 仓库，分支 release.new）
│   │   ├── after_process_data/           # 165 个 *.xlsx（训练数据）
│   │   ├── code/                         # 9 个独立训练脚本
│   │   ├── model/                        # 空（模型权重不入库）
│   │   └── util/concat_data.py           # 数据合并工具
│   ├── sleep_stage/睡眠研究/SleepEDF数据处理/  # 睡眠分期（3 子工程，不在 git 下）
│   │   ├── IMU_sleep_stage-带有标签的IMU代码处理/
│   │   ├── Sleep-pdf处理代码/new_project/    # 最新工程
│   │   └── sleep_stage-迁移标签代码/         # 整合入口所在
│   └── sleep_edf数据集/                  # Sleep-EDF 公开数据集（RECORDS, *.edf）
├── tools/                                # 工具脚本（4 个）
├── docs/superpowers/                     # 分析报告/计划/设计文档
└── .gitignore                            # 数据/模型/嵌套 git 已排除
```

## 关键陷阱

| 陷阱 | 说明 | 位置 |
|------|------|------|
| Windows 硬编码路径 | 至少 4 文件含 `F:/...` 路径，macOS/Linux 失效 | `sleep_stage/.../code-数据处理的代码/`、`data_deal_code/` |
| 环境缺失依赖 | 本地无 torch/sklearn/pandas，import 即 ImportError | 训练需远程服务器 |
| 嵌套 git 仓库 | `sleep_classify/` 自有 `.git`（分支 `release.new`） | 改代码前先 `git status` |
| 中文文件名/路径 | 含空格、括号、汉字，shell 需引号包裹 | `sleep_stage/` 全目录 |
| 拼写错误文件名 | **不要"修正"**：`descison_tree`、`logic_regresssion`、`rnn_classfiy` | `code/` 目录 |

## 数据布局

### 睡姿分类（posture）
- **原始数据**: `after_process_data/after_process_data/` 下 165 个 `*.xlsx`
- **标签规则**: `left`=0（左侧卧）、`m`=1（仰卧）、`right`=2（右侧卧）；`*_motion.xlsx` 不参与训练
- **特征**: 6 列 IMU 特征 `feature1-feature6`（3 加速度 + 3 角速度）
- **训练脚本**: `code/` 下 9 个独立入口，无统一 `train.py`
- **⚠️ 标签约定不一致**: `kdtree_data.py` 使用 `{1: left, 2: m, 3: right}`，其他脚本使用 `{0: left, 1: m, 2: right}`。历史遗留，暂不修复。

### 睡眠分期（sleep stage）- 3 子工程
- **IMU 标签**: `IMU_sleep_stage.../base_data/` 含 `train_label.csv`、`liu_imu_label.csv` 等
- **标签迁移**: `sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/integrate_deal_process-只看这个代码.py` 为整合入口
- **Sleep-pdf**: `Sleep-pdf处理代码/new_project/` 最新工程，含 `psg_*.py` 模型 + `merge_data/` CSV
- **被试**: chy、gjx、liu 三人，每人有对应 EEG + IMU 原始 `.xls` 文件

## 约定

- **中文注释/docstring** 普遍，类名/变量名英文 — 不要翻译
- **超参数默认值**: epochs=100、batch_size=128、lr=0.001（Adam）、random_state=42、test_size=0.2
- **入口**: `if __name__ == "__main__"` 为主；`bp_algorithm.py` 额外提供 `t0()` 函数
- **运行目录**: 每个脚本从自身所在目录执行（依赖 `../xxx` 相对路径）

## 反模式（此项目特有）

- **`except: pass`** — 多个文件有空 except 块，静默吞掉数据加载错误
- **绝对 Windows 路径** — 硬编码 `F:/master_paper_and_project/...`，不可移植
- **依赖缺失** — 本地无 ML 包，需远程环境
- **git 外关键文件** — `sleep_stage/` 全目录不受 git 管理，需手动备份

## 命令

```bash
# 睡姿训练（从 code/ 目录执行）
cd graduation_transfer/sleep_posture/sleep_classify/code
python bp_algorithm.py

# 运行分析工具
python tools/run_analysis.py

# 健康检查
python tools/script_health_check.py
```

## 远程工作流

训练在 `root@159.75.177.109:22` 或 PyCharm `Python 3.7 (pytorch)` 环境执行。本地只做编辑和小规模验证。
