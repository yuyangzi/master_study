# 脚本可运行性报告 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 跑 29 个新修过路径的 sleep_stage 脚本，结合 17:12 run_results.json 中 5 条 sleep_classify 实跑数据，生成 `docs/superpowers/reports/2026-06-06-script-runnability-report.md` — 48 个 .py 脚本（49 真实 - 1 跳过 = 48，+1 漏网 `data_deal/test.py`）的可运行性全量报告（含功能一句话、失败原因、修复提示、行号、修复优先级）

**Architecture:** 两层 — Layer 1 扩展 `tools/run_analysis.py` 加 `--filter` 参数跑 29 个 sleep_stage 脚本输出新 JSON；Layer 2 新建 `tools/generate_runnability_report.py` 读两份 JSON + 静态扫描 48 个 .py 渲染 Markdown 报告

**Tech Stack:** Python 3.11 stdlib only（ast / json / subprocess / re / dataclasses / pathlib），无第三方依赖

---

## Task 1: 扩展 run_analysis.py — 添加 CLI 参数

**Files:**
- Modify: `tools/run_analysis.py:15` (CLI 解析)
- Modify: `tools/run_analysis.py:29` (SCRIPTS 列表定义)

### Step 1.1: 添加 argparse CLI 解析

在文件顶部（`import` 之后、`WORKSPACE = ...` 之前）替换：

```python
WORKSPACE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
os.chdir(WORKSPACE)
```

替换为：

```python
import argparse

WORKSPACE_DEFAULT = Path.cwd()

def parse_args():
    parser = argparse.ArgumentParser(
        description="批量运行分析工具 — 逐一执行 Python 脚本，收集 stdout/stderr/exit_code"
    )
    parser.add_argument("workspace", nargs="?", default=None,
                        help="workspace 目录（默认 cwd）")
    parser.add_argument("--filter", choices=["all", "sleep_classify", "sleep_stage"],
                        default="all", help="脚本发现过滤器（默认 all）")
    parser.add_argument("--output", default=None,
                        help="JSON 输出文件路径（默认按 filter 自动命名）")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅打印发现列表 + OUTPUT 路径，不实际执行")
    parser.add_argument("--print-output", action="store_true",
                        help="仅打印 OUTPUT 路径（配合 --dry-run 使用）")
    return parser.parse_args()

ARGS = parse_args()
WORKSPACE = Path(ARGS.workspace).resolve() if ARGS.workspace else WORKSPACE_DEFAULT
os.chdir(WORKSPACE)
```

并在 `import argparse` 之后保留其他 import 不动。

### Step 1.2: 替换 SCRIPTS 列表的发现逻辑

将 `tools/run_analysis.py:29-78`（整个 `SCRIPTS = [...]` 列表，**正好在 `def run_one` 之前结束**）替换为按 filter 动态发现的代码。

在 `SCRIPTS = [...]` 之后（紧接 `OUTPUT = ...` 那行之前）插入：

```python
# ── 脚本发现（按 filter） ──────────────────────────────────────────
GRADUATION = WORKSPACE / "graduation_transfer"
SCRIPTS_ALL = [
    # ====== sleep_classify/code/ ======
    (GRADUATION / "sleep_posture/sleep_classify/code/SVM_algorithm.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_FAST, "SVM_algorithm"),
    (GRADUATION / "sleep_posture/sleep_classify/code/bp_algorithm.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_DL, "bp_algorithm"),
    (GRADUATION / "sleep_posture/sleep_classify/code/descison_tree.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_FAST, "descison_tree"),
    (GRADUATION / "sleep_posture/sleep_classify/code/kdtree_data.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_FAST, "kdtree_data"),
    (GRADUATION / "sleep_posture/sleep_classify/code/kmeans_algorithm.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_FAST, "kmeans_algorithm"),
    (GRADUATION / "sleep_posture/sleep_classify/code/logic_regresssion.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_FAST, "logic_regresssion"),
    (GRADUATION / "sleep_posture/sleep_classify/code/lstm_classify.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_DL, "lstm_classify"),
    (GRADUATION / "sleep_posture/sleep_classify/code/rnn_classfiy.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_DL, "rnn_classfiy"),
    (GRADUATION / "sleep_posture/sleep_classify/code/transformer_classify.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_DL, "transformer_classify"),
    (GRADUATION / "sleep_posture/sleep_classify/code/verify_model.py",
     GRADUATION / "sleep_posture/sleep_classify/code", TIMEOUT_FAST, "verify_model"),
    (GRADUATION / "sleep_posture/sleep_classify/util/concat_data.py",
     GRADUATION / "sleep_posture/sleep_classify/util", TIMEOUT_CONCAT, "concat_data"),
    # ====== Sleep-pdf (clean) ======
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/bar_chart.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "bar_chart"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/model_figure.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "model_figure"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/new__hybird_imag.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "new__hybird_imag"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/serial_port_extract.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal",
     TIMEOUT_FAST, "serial_port_extract"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/test_psg_data.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理",
     TIMEOUT_FAST, "test_psg_data"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/test.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal",
     TIMEOUT_FAST, "origin_test"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/test_all.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)",
     TIMEOUT_FAST, "test_all"),
    # ====== sleep_stage (新修路径) — 仅在 filter=sleep_stage 时使用 ======
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/cal_label_count.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code",
     TIMEOUT_FAST, "cal_label_count"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/data_deal.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code",
     TIMEOUT_FAST, "data_deal"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/smote_label.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code",
     TIMEOUT_FAST, "smote_label"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/train_data_deal.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code",
     TIMEOUT_FAST, "train_data_deal"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_cnn.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model",
     TIMEOUT_DL, "imu_cnn"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_cnn_lstm.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model",
     TIMEOUT_DL, "imu_cnn_lstm"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_cnn_rnn.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model",
     TIMEOUT_DL, "imu_cnn_rnn"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_kdtree.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model",
     TIMEOUT_FAST, "imu_kdtree"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_lstm.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model",
     TIMEOUT_DL, "imu_lstm"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_lstm_rnn.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model",
     TIMEOUT_DL, "imu_lstm_rnn"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model/imu_rnn.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model",
     TIMEOUT_DL, "imu_rnn"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/add_imu_label_4.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)",
     TIMEOUT_FAST, "add_imu_label_4"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/eeg_data_add_label_3.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)",
     TIMEOUT_FAST, "eeg_data_add_label_3"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/eeg_data_deal_1.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)",
     TIMEOUT_FAST, "eeg_data_deal_1"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/eeg_data_to_base_2.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)",
     TIMEOUT_FAST, "eeg_data_to_base_2"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/imu_data_deal_1.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)",
     TIMEOUT_FAST, "imu_data_deal_1"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/integrate_deal_process-只看这个代码.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)",
     TIMEOUT_FAST, "integrate_deal_process"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/model/psg_rnn_lstm.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/model",
     TIMEOUT_DL, "psg_rnn_lstm"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/balance_data-提取后数据的预处理.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理",
     TIMEOUT_FAST, "balance_data"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/new_feature_deal-EEG提取.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理",
     TIMEOUT_FAST, "new_feature_deal"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/raw_data_extract.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理",
     TIMEOUT_FAST, "raw_data_extract"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/basic_rnn.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_DL, "basic_rnn"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/decsion_tree.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "decsion_tree"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/hybird_matrix.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "hybird_matrix"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_cnn.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_DL, "psg_cnn"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_kdtree.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "psg_kdtree"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_knn.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "psg_knn"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_lstm.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_DL, "psg_lstm"),
    (GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/psg_rnn_lstm.py",
     GRADUATION / "sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_DL, "psg_rnn_lstm"),
]

# ── 过滤器 ──────────────────────────────────────────
if ARGS.filter == "all":
    SCRIPTS = SCRIPTS_ALL
elif ARGS.filter == "sleep_classify":
    SCRIPTS = SCRIPTS_ALL[:18]
elif ARGS.filter == "sleep_stage":
    SCRIPTS = SCRIPTS_ALL[18:]
```

注意：`SCRIPTS = [...]` 现有的 18 条手写列表**先删掉**，再用上面的 `SCRIPTS_ALL` 替代。文件中现有的 18 条已通过 `SCRIPTS_ALL[:18]` 包含。

**SCRIPTS_ALL 计数核对**（实盘 `find graduation_transfer -name "*.py" | grep -v __init__ | grep -v feature_deal` = **48 条**）：
- 18 sleep_classify（11 sleep_classify + 7 sleep_stage 旧）= 18 条
- 29 sleep_stage 新修路径 = 29 条
- 1 sleep_stage 漏网（`data_deal-sleep-pdf原始数据处理/test.py`）= **不在 SCRIPTS_ALL**，但 `discover_scripts()` 会发现，报告里以 "not-run" 出现
- 总计 `len(SCRIPTS_ALL) = 47`，`discover_scripts() = 48`

**Stem 冲突清单**（已处理 — 使用 `rel_path` 作为 dict key 避免覆盖）：
- `psg_rnn_lstm` 在 2 个目录：`睡眠研究/.../sleep_stage-迁移标签代码/model/` 和 `Sleep-pdf处理代码/new_project/model-模型训练代码/`
- `test` 在 2 个目录：`data_deal-sleep-pdf原始数据处理/test.py` 和 `origin_data_deal/test.py`（用 label `origin_test` 区分）

### Step 1.3: 添加输出文件名自动命名

**现有 `run_analysis.py` 实际结构**（grep 验证）：
- 模块级别无 `OUTPUT` 变量
- `output_path = WORKSPACE / "docs/superpowers/reports/run_results.json"` 出现在 `main()` 函数内部（line 182）
- `main()` 还在最后调用 `generate_report(results, report_path)` 生成旧的 markdown 报告

**修改方案**：

1. 在 SCRIPTS_ALL 之后、过滤器之前（module level）添加 OUTPUT 计算逻辑：

```python
# ── 输出路径（按 filter） ──────────────────────────────────────
def _compute_output() -> Path:
    if ARGS.output:
        return Path(ARGS.output).resolve()
    if ARGS.filter == "sleep_classify":
        return WORKSPACE / "docs/superpowers/reports/run_results-sleep_classify.json"
    if ARGS.filter == "sleep_stage":
        return WORKSPACE / "docs/superpowers/reports/run_results-sleep_stage.json"
    return WORKSPACE / "docs/superpowers/reports/run_results.json"

OUTPUT = _compute_output()
```

2. 在 `main()` 函数内（line 182）将 `output_path = WORKSPACE / "docs/superpowers/reports/run_results.json"` 改为：

```python
output_path = OUTPUT  # ← 用模块级 OUTPUT（按 filter 自动命名）
```

3. **`--filter sleep_stage` 跳过旧 markdown 报告**（避免与新报告混淆）：

在 `main()` 函数最后（`generate_report(...)` 调用之前）添加：

```python
# 仅在 --filter all 或 --filter sleep_classify 时生成旧 markdown 报告
# --filter sleep_stage 不生成（避免与新 runnability 报告混淆）
if ARGS.filter != "sleep_stage":
    generate_report(results, report_path)
```

### Step 1.4: 修改 `rel_path` 计算

文件中所有引用 `Path(rd).relative_to(WORKSPACE)` 的地方（如 `rel_path = Path(r["script"]).relative_to(WORKSPACE)`）保持不变。但需要确认 `Path(r["script"])` 接受 `SCRIPTS_ALL` 里的 `Path` 对象（应该可以）：

```python
"script": str(scripts[i][0]),  # Path -> str
"workdir": str(scripts[i][1]),
```

如果原代码是 `Path(...).resolve()` 然后再 `relative_to(WORKSPACE)`，新代码改成直接 `str(scripts[i][0])` 即可。

如果发现 `rel_path` 计算报错，**保持原样不修改**，转而把 `script` 字段在写入时统一 `str(scripts[i][0])`。

### Step 1.5: 验证向后兼容（无参数跑）

Run:
```bash
cd /Users/zero/Desktop/master_study
master_study_env/bin/python tools/run_analysis.py --help
```

Expected: 输出 argparse help，显示 `--filter {all,sleep_classify,sleep_stage}` 和 `--output` 选项。

如果失败：检查 `import argparse` 是否在文件顶部。

### Step 1.6: 验证 --filter sleep_stage 发现恰好 29 个脚本

Run:
```bash
cd /Users/zero/Desktop/master_study
master_study_env/bin/python tools/run_analysis.py --filter sleep_stage --dry-run 2>&1 | head -40
```

Expected: 打印 `Loaded 29 sleep_stage scripts` + 29 行 `label: filename` 列表

**实现要求**：必须在 `main()` 函数中（Step 1.3 修改的 `output_path` 之前）添加 `--dry-run` 短路逻辑：

```python
if ARGS.dry_run:
    print(f"Loaded {len(SCRIPTS)} {ARGS.filter} scripts")
    for s in SCRIPTS:
        print(f"  {s[3]:30s} {s[0].name}")
    if ARGS.print_output:
        print(f"output: {OUTPUT}")
    return
```

否则 29 个脚本会被直接跑一遍（~15 分钟）。

如果不足/超过 29：检查 `SCRIPTS_ALL[18:]` 的 29 条是否都存在（路径必须在 macOS 上 resolve 成功）。

> **避开 importlib mock 的坑**：`spec.loader.exec_module()` 会执行模块顶层代码（包括全局 `if __name__ == "__main__": main()` 块），而 argparse 一旦参数解析失败就会 `sys.exit(2)`。改用 `subprocess.run([sys.executable, "tools/run_analysis.py", "--filter", "sleep_stage", "--dry-run"])` 替代旧计划里的 importlib mock。

### Step 1.7: 验证输出文件名命名

Run:
```bash
cd /Users/zero/Desktop/master_study
master_study_env/bin/python tools/run_analysis.py --filter sleep_stage --dry-run --print-output 2>&1 | tail -3
```

Expected: `output: /Users/zero/Desktop/master_study/docs/superpowers/reports/run_results-sleep_stage.json`

**实现要求**：与 Step 1.6 同样用 `--dry-run` + `--print-output`（仅打印 OUTPUT 路径，不写文件），避开 importlib mock 副作用。Step 1.6 的代码片段里已经有 `if ARGS.print_output: print(f"output: {OUTPUT}")` 这一行。

---

## Task 2: 跑 29 个 sleep_stage 脚本

**Files:**
- Create: `docs/superpowers/reports/run_results-sleep_stage.json` (执行结果)

### Step 2.1: 启动批量执行

Run:
```bash
cd /Users/zero/Desktop/master_study
master_study_env/bin/python tools/run_analysis.py --filter sleep_stage 2>&1 | tee /tmp/run_stage.log
```

**期望**：
- 29 个脚本逐个执行，每个 ~10-60s（DL 脚本 120s）
- 终端实时打印每个脚本的 `label`, `exit_code`, `duration_s`, `summary`
- SCRIPTS_ALL[18:] 包含 **11 个** `TIMEOUT_DL` (300s) 脚本（imu_cnn/lstm/rnn 6 个、迁移 psg_rnn_lstm、Sleep-pdf basic_rnn/psg_cnn/psg_lstm/psg_rnn_lstm 4 个）。如果每个跑满 300s 才失败，DL 部分就要 11×5min = 55 分钟；剩余 ~18 个 FAST 脚本按 ~1-2 min 算 18-36 分钟
- **预计总耗时 ~60-90 分钟**（之前估计的 15-30 分钟过于乐观）
- 全部完成后写 `docs/superpowers/reports/run_results-sleep_stage.json`

**不要**在跑完前打断。如果某脚本导致卡死超过 120s，自动 timeout。

### Step 2.2: 验证 JSON 输出

Run:
```bash
cd /Users/zero/Desktop/master_study
master_study_env/bin/python -c "
import json
d = json.load(open('docs/superpowers/reports/run_results-sleep_stage.json'))
print(f'entries: {len(d)}')
status_count = {}
for r in d:
    s = r.get('summary', '?').split(' — ')[0]
    status_count[s] = status_count.get(s, 0) + 1
for s, c in sorted(status_count.items()):
    print(f'  {s}: {c}')
"
```

Expected: `entries: 29` + 各状态计数（应包含 `✅ 成功`、`❌ 失败`、`⏱ 超时` 等）

### Step 2.3: 检查失败原因分布

Run:
```bash
cd /Users/zero/Desktop/master_study
master_study_env/bin/python -c "
import json
from collections import Counter
d = json.load(open('docs/superpowers/reports/run_results-sleep_stage.json'))
errors = Counter()
for r in d:
    if r.get('error_type'):
        errors[r['error_type']] += 1
for e, c in errors.most_common():
    print(f'  {e}: {c}')
"
```

Expected: 列出 `FileNotFoundError`/`ModuleNotFoundError`/`RuntimeError` 等的分布

---

## Task 3: 创建 generate_runnability_report.py

**Files:**
- Create: `tools/generate_runnability_report.py` (~250 行)

### Step 3.1: 写文件头部 + 数据结构

新建 `tools/generate_runnability_report.py`：

```python
#!/usr/bin/env python3
"""
生成 48 个 .py 脚本的可运行性报告（49 个真实脚本 - 1 跳过）。
读两份 run_results JSON + 静态扫描 .py 文件，输出 Markdown。

用法: master_study_env/bin/python tools/generate_runnability_report.py [WORKSPACE]
"""
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

WORKSPACE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

# ── 数据结构 ──────────────────────────────────────────
@dataclass
class ScriptInfo:
    label: str
    rel_path: str
    group: str
    purpose: str
    imports: list[str] = field(default_factory=list)
    has_main: bool = False
    run_status: str = "not-run"   # success / failed / timeout / skipped / not-run
    exit_code: Optional[int] = None
    duration_s: float = 0.0
    error_type: Optional[str] = None
    error_summary: Optional[str] = None
    error_line: Optional[int] = None
    fix_hint: str = ""
    priority: str = ""            # P0-快 / P1-中 / P2-数据 / P3-GPU / P4-可忽略
    data_source: str = ""         # "" (未跑) / "old" (17:12 JSON) / "new" (本次)
```

### Step 3.2: 写子项目分组 & 脚本发现

在数据类之后：

```python
# ── 子项目分组（按相对路径前缀） ──────────────────────────
GROUP_PATTERNS = [
    ("sleep_classify", "graduation_transfer/sleep_posture/sleep_classify/"),
    ("IMU",             "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage"),
    ("迁移",            "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/"),
    ("Sleep-pdf/data",  "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-"),
    ("Sleep-pdf/model", "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-"),
    ("Sleep-pdf/origin","graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/"),
]

def classify_group(rel: str) -> str:
    for label, pat in GROUP_PATTERNS:
        if pat in rel:
            return label
    return "other"

# ── 脚本发现 ──────────────────────────────────────────
def discover_scripts() -> list[Path]:
    grad = WORKSPACE / "graduation_transfer"
    out = []
    for py in grad.rglob("*.py"):
        if py.name == "__init__.py":
            continue
        if py.name == "feature_deal.py":  # 全注释伪 .py，跳过
            continue
        out.append(py)
    return sorted(out)
```

### Step 3.3: 写"功能一句话"提取

```python
# ── "功能一句话"提取规则 ──────────────────────────────
def extract_purpose(path: Path) -> str:
    try:
        src = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"(无法读取: {e})"

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return f"(语法错误: {e.msg})"

    # 规则 1: module docstring
    doc = ast.get_docstring(tree)
    if doc:
        first = re.split(r"[。.!?!？\n]", doc.strip(), maxsplit=1)[0].strip()
        if first and len(first) >= 4:
            return first[:80]

    # 规则 2: if __name__ == "__main__": 块首字符串
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if (isinstance(test, ast.Compare) and
                isinstance(test.left, ast.Name) and test.left.id == "__name__" and
                len(test.comparators) == 1 and
                isinstance(test.comparators[0], ast.Constant) and
                test.comparators[0].value == "__main__"):
                for sub in node.body:
                    if isinstance(sub, ast.Expr) and isinstance(sub.value, ast.Constant):
                        if isinstance(sub.value.value, str) and len(sub.value.value) > 3:
                            return sub.value.value[:80]
                break

    # 规则 3: 文件名 + imports 启发式
    name = path.stem.lower()
    imports = extract_imports(tree)
    if "train" in name:
        return f"训练机器学习模型（{', '.join(imports[:3])}）"
    if "deal" in name or "preprocess" in name:
        return f"数据预处理脚本（{', '.join(imports[:3])}）"
    if "extract" in name:
        return f"数据提取脚本（{', '.join(imports[:3])}）"
    if "chart" in name or "figure" in name or "imag" in name:
        return "生成可视化图表/混淆矩阵"
    if "test" in name:
        return "测试/验证脚本"
    if "count" in name:
        return "统计/计数脚本"

    return "(无法推断)"

def extract_imports(tree: ast.AST) -> list[str]:
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
    return sorted(mods)

def has_main_block(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if (isinstance(test, ast.Compare) and
                isinstance(test.left, ast.Name) and test.left.id == "__name__" and
                len(test.comparators) == 1 and
                isinstance(test.comparators[0], ast.Constant) and
                test.comparators[0].value == "__main__"):
                return True
    return False
```

### Step 3.4: 写错误行号提取 & 修复提示模板

```python
# ── 错误行号提取 ──────────────────────────────────────
_LINE_RE = re.compile(r'line (\d+), in <module>')

def extract_error_line(stderr: str) -> Optional[int]:
    m = _LINE_RE.search(stderr)
    return int(m.group(1)) if m else None

# ── 修复提示模板 ──────────────────────────────────────
def make_fix_hint(error_type: str, error_detail: str, error_line: Optional[int]) -> str:
    line_str = f"第 {error_line} 行" if error_line else "相应位置"
    et = (error_type or "").lower()
    if "nameerror" in et:
        m = re.search(r"name '(\w+)'", error_detail or "")
        var = m.group(1) if m else "X"
        return f"变量 `{var}` 未定义。原因：可能未初始化或被注释。修复：{line_str} 附近加 `{var} = ...`"
    if "prefetch_factor" in (error_detail or ""):
        return f"PyTorch 2.x 不允许 num_workers=0 时设 prefetch_factor。修复：{line_str} 的 `DataLoader(...)` 删除 `prefetch_factor=2` 参数"
    if "too many dimensions" in (error_detail or ""):
        return f"pandas Series 直接喂 torch.tensor 报错。修复：{line_str} `torch.tensor(y_train)` 改为 `torch.tensor(y_train.values)`"
    if "liblinear" in (error_detail or "") and "multiclass" in (error_detail or ""):
        return f"liblinear 不支持 3 分类。修复：{line_str} `solver='liblinear'` 改为 `solver='lbfgs'`"
    if "sheet is too large" in (error_detail or ""):
        return f"Excel 行数超过 1048576 上限。修复：{line_str} `df.to_excel(...)` 改为 `df.to_csv(...)` 或拆 sheet"
    if "filenotfounderror" in et:
        if "kd_tree.m" in (error_detail or ""):
            return "模型未训练。修复：先跑 kdtree_data.py 生成 ../model/kd_tree.m"
        if any(x in (error_detail or "") for x in [".txt", ".csv", ".hex", ".edf"]):
            return "IMU 原始数据缺失。修复：把被试数据放到 data/ 目录，或检查 Path(__file__) 推导是否正确"
        return "数据文件不存在。修复：检查路径或补充数据"
    if "modulenotfounderror" in et:
        m = re.search(r"No module named '(\S+)'", error_detail or "")
        mod = m.group(1) if m else "?"
        return f"缺包。修复：`pip install {mod}`"
    if "timeout" in et:
        return "训练耗时长。修复：加长 timeout（如 600s）或减少数据量/epochs"
    return "(手工诊断)"
```

### Step 3.5: 写优先级判定

```python
# ── 优先级判定（先匹配先赢） ──────────────────────────
def classify_priority(info: ScriptInfo, path: Path) -> str:
    src = path.read_text(encoding="utf-8") if path.exists() else ""
    # P4: 全注释伪 .py
    if not info.imports and ("# " in src or "#" in src) and "def " not in src:
        return "⚪ P4-可忽略"
    # P4: 无 main 且无 I/O 副作用
    if not info.has_main and "open(" not in src and "to_csv" not in src and "to_excel" not in src:
        return "⚪ P4-可忽略"
    # P3: torch + 训练循环
    if "torch" in info.imports and ("range(" in src or "for epoch" in src.lower()):
        return "🔵 P3-GPU"
    # P2: FileNotFoundError
    if info.error_type and "filenotfounderror" in info.error_type.lower():
        return "🟠 P2-数据"
    # P0: 单行修复
    if info.error_type in ("NameError",) or any(k in (info.error_summary or "")
            for k in ["prefetch_factor", "liblinear", "sheet is too large", "too many dimensions"]):
        return "🟢 P0-快"
    # P1: 其余
    return "🟡 P1-中"
```

### Step 3.6: 写 JSON 合并 + 扫描 48 个脚本

```python
# ── 合并两份 JSON ──────────────────────────────────────
def load_results() -> list[dict]:
    """合并两份 run_results JSON；缺失/解析失败时返回空 list 不抛错。"""
    out = []
    old = WORKSPACE / "docs/superpowers/reports/run_results.json"          # 17:12 5 条 sleep_classify
    new = WORKSPACE / "docs/superpowers/reports/run_results-sleep_stage.json"  # 29 条（本次）
    for f, tag in [(old, "old"), (new, "new")]:
        if not f.exists():
            print(f"WARN: {f.name} not found, skipping", file=sys.stderr)
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"WARN: {f.name} parse error: {e}", file=sys.stderr)
            continue
        for r in data:
            r["data_source"] = tag
            out.append(r)
    return out

# ── 扫描所有 48 个脚本 ──────────────────────────────────
def scan_all_scripts() -> dict[str, ScriptInfo]:
    """key = rel_path（绝对唯一），避免 psg_rnn_lstm / test 这样的 stem 冲突覆盖。"""
    out = {}
    for path in discover_scripts():
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except Exception:
            tree = None
            src = ""
        rel = str(path.relative_to(WORKSPACE))
        info = ScriptInfo(
            label=path.stem,
            rel_path=rel,
            group=classify_group(rel),
            purpose=extract_purpose(path) if tree else "(语法错误)",
            imports=extract_imports(tree) if tree else [],
            has_main=has_main_block(tree) if tree else False,
        )
        out[rel] = info  # ← 用 rel_path 作 key（不是 path.stem）
    return out
```

### Step 3.7: 合并执行结果到 ScriptInfo

```python
# ── 把执行结果合并到 ScriptInfo ──────────────────────────
def merge_results(scripts: dict[str, ScriptInfo], results: list[dict]):
    """匹配顺序：rel_path 精确 > rel_path 末段 > label 字符串。
    覆盖了「旧 JSON 5 条 label 命名不一致」「psg_rnn_lstm 同名」「test 同名」三类场景。
    """
    # 1) 构建 rel_path 末段 -> info 的反向索引
    by_stem_suffix: dict[str, ScriptInfo] = {
        Path(k).name: v for k, v in scripts.items()
    }

    matched = 0
    for r in results:
        # JSON 里 script 字段是绝对路径，转 rel_path
        r_rel = str(Path(r["script"]).relative_to(WORKSPACE))
        info = None
        # 1) 精确匹配 rel_path
        if r_rel in scripts:
            info = scripts[r_rel]
        # 2) 末段文件名匹配（应对"p只存了 stem 不是 rel_path"的老 JSON）
        elif Path(r_rel).name in by_stem_suffix:
            info = by_stem_suffix[Path(r_rel).name]
        # 3) 退化：按 label 字符串匹配
        elif r.get("label") in [i.label for i in scripts.values()]:
            info = next(i for i in scripts.values() if i.label == r["label"])
        if info is None:
            print(f"WARN: no script match for {r_rel} (label={r.get('label')})", file=sys.stderr)
            continue
        matched += 1
        info.run_status = "success" if r.get("exit_code") == 0 and not r.get("timeout") else \
                          "timeout" if r.get("timeout") else "failed"
        info.exit_code = r.get("exit_code")
        info.duration_s = r.get("duration_s", 0.0)
        info.error_type = r.get("error_type")
        info.error_summary = (r.get("error_detail") or "")[:200]
        info.error_line = extract_error_line(r.get("stderr", ""))
        # 成功脚本不需要修复提示（make_fix_hint(None,...) 会返回 "(手工诊断)"，会误导）
        info.fix_hint = (
            make_fix_hint(info.error_type, r.get("error_detail", ""), info.error_line)
            if info.run_status != "success" else ""
        )
        info.data_source = r.get("data_source", "old")
    print(f"merge_results: matched {matched}/{len(results)} run entries", file=sys.stderr)

    # 优先级判定
    for rel, info in scripts.items():
        full_path = WORKSPACE / info.rel_path
        info.priority = classify_priority(info, full_path)
```

### Step 3.8: 写 Markdown 渲染

```python
# ── Markdown 渲染 ──────────────────────────────────────
def render_markdown(scripts: dict[str, ScriptInfo]) -> str:
    lines = []
    w = lines.append

    w("# 脚本可运行性报告")
    w("")
    w("- 运行时间: 2026-06-06")
    w("- 范围: graduation_transfer/ 48 个 .py 脚本（49 个真实脚本 - 1 跳过 = 48；额外 1 条 `data_deal/test.py` 在磁盘但不在 SCRIPTS_ALL）")
    w("- 数据源: 5 旧 (17:12 run_results.json) + 29 新 (本次) + 14 未跑 + 1 跳过（feature_deal.py）")
    w("- 环境: master_study_env (Python 3.11, macOS ARM64, torch 2.12 CPU)")
    w("")

    # 汇总
    status_count = {"success": 0, "failed": 0, "timeout": 0, "skipped": 0, "not-run": 0}
    priority_count = {"🟢 P0-快": 0, "🟡 P1-中": 0, "🟠 P2-数据": 0, "🔵 P3-GPU": 0, "⚪ P4-可忽略": 0}
    for info in scripts.values():
        status_count[info.run_status] = status_count.get(info.run_status, 0) + 1
        priority_count[info.priority] = priority_count.get(info.priority, 0) + 1
    # 硬编码 1 跳过（feature_deal.py）— 它在 discover_scripts() 中被过滤掉，不会出现在 scripts 字典里
    status_count["skipped"] = 1

    w("## 汇总")
    w("")
    w("| 状态 | 数量 |")
    w("|---|---|")
    w(f"| ✅ 运行成功 | {status_count['success']} |")
    w(f"| ❌ 失败 | {status_count['failed']} |")
    w(f"| ⏱ 超时 | {status_count['timeout']} |")
    w(f"| ⚠️ 跳过 | {status_count['skipped']} |（feature_deal.py 全注释）")
    w("")

    w("## 修复优先级")
    w("")
    w("| 优先级 | 数量 | 处理建议 |")
    w("|---|---|---|")
    w(f"| 🟢 P0-快 | {priority_count['🟢 P0-快']} | 现在修，~5 分钟 |")
    w(f"| 🟡 P1-中 | {priority_count['🟡 P1-中']} | 今天修，~30 分钟 |")
    w(f"| 🟠 P2-数据 | {priority_count['🟠 P2-数据']} | 数据到位后修 |")
    w(f"| 🔵 P3-GPU | {priority_count['🔵 P3-GPU']} | 上服务器跑 |")
    w(f"| ⚪ P4-可忽略 | {priority_count['⚪ P4-可忽略']} | 视情况 |")
    w("")

    # 按 group 分节
    group_order = ["sleep_classify", "IMU", "迁移", "Sleep-pdf/data", "Sleep-pdf/model", "Sleep-pdf/origin"]
    for grp in group_order:
        members = [info for info in scripts.values() if info.group == grp]
        if not members:
            continue
        w(f"### {grp}（{len(members)} 条）")
        w("")
        for info in sorted(members, key=lambda x: x.label):
            render_script(w, info)
            w("")

    # 跳过的脚本
    w("### 跳过的脚本")
    w("")
    w("- `feature_deal.py` — 全注释伪 .py，136 行全部注释")
    w("")

    # 附录
    w("## 附录")
    w("")
    w("- 跑 29 个脚本: `tools/run_analysis.py --filter sleep_stage`")
    w("- 重新生成报告: `tools/generate_runnability_report.py`")
    w("- 旧 run_results.json: 17:12 5 条 sleep_classify 验证")
    w("- 旧 run-analysis-report.md: 15:29 18 个完整分析（markdown，无法结构化合并）")
    w("")
    return "\n".join(lines)

def render_script(w, info: ScriptInfo):
    icon = {"success": "✅", "failed": "❌", "timeout": "⏱", "skipped": "⚠️", "not-run": "❔"}.get(info.run_status, "❔")
    w(f"#### {icon} `{info.label}.py`")
    w("")
    w(f"- 路径: `{info.rel_path}`")
    w(f"- 功能: {info.purpose}")
    w(f"- Imports: {', '.join(info.imports[:5]) or '(空)'}")
    if info.run_status != "not-run":
        w(f"- 运行: exit={info.exit_code}, {info.duration_s:.1f}s")
    if info.error_type:
        w(f"- 错误: `{info.error_type}: {info.error_summary}`")
    if info.error_line:
        w(f"- 行号: {info.error_line}")
    if info.fix_hint:
        w(f"- 修复: {info.fix_hint}")
    if info.priority:
        w(f"- 优先级: {info.priority}")
    if info.data_source:
        w(f"- 数据源: {'新 (本次)' if info.data_source == 'new' else '旧 (17:12 JSON)'}")
    w("")
```

### Step 3.9: 写 main

```python
def main():
    scripts = scan_all_scripts()
    results = load_results()
    merge_results(scripts, results)

    md = render_markdown(scripts)
    out = WORKSPACE / "docs/superpowers/reports/2026-06-06-script-runnability-report.md"
    out.write_text(md, encoding="utf-8")
    print(f"Report written to {out}")
    print(f"Total scripts: {len(scripts)}")
    status_count = {"success": 0, "failed": 0, "timeout": 0, "skipped": 0, "not-run": 0}
    for info in scripts.values():
        status_count[info.run_status] = status_count.get(info.run_status, 0) + 1
    # 硬编码 1 跳过（feature_deal.py）— 它在 discover_scripts() 中被过滤掉，不会出现在 scripts 字典里
    status_count["skipped"] = 1
    for s, c in status_count.items():
        print(f"  {s}: {c}")

if __name__ == "__main__":
    main()
```

### Step 3.10: 运行报告生成器

Run:
```bash
cd /Users/zero/Desktop/master_study
master_study_env/bin/python tools/generate_runnability_report.py
```

Expected: 终端打印 `Report written to .../2026-06-06-script-runnability-report.md` + 状态计数

如果 `load_results()` 找不到新 JSON：先回 Task 2 跑 29 个脚本。

### Step 3.11: 验证报告内容

Run:
```bash
cd /Users/zero/Desktop/master_study
wc -l docs/superpowers/reports/2026-06-06-script-runnability-report.md
master_study_env/bin/python -c "
import re
md = open('docs/superpowers/reports/2026-06-06-script-runnability-report.md').read()
print('scripts with status:', len(re.findall(r'^#### ', md, re.M)))
print('P0:', md.count('🟢 P0-快'))
print('P1:', md.count('🟡 P1-中'))
print('P2:', md.count('🟠 P2-数据'))
print('P3:', md.count('🔵 P3-GPU'))
print('P4:', md.count('⚪ P4-可忽略'))
"
```

Expected:
- 报告 ~500-900 行
- 脚本数 48（`discover_scripts()` 实际发现数）
- 优先级计数合理（5 个标签都有 ≥1 个）

### Step 3.12: 抽样核对 3 个失败脚本的修复提示

抽样 `kdtree_data`（old 旧 JSON 有数据）、`smote_label`（new 29 个新跑数据）、`verify_model`（old 旧 JSON 有数据）三个（覆盖两个数据源）：

```bash
cd /Users/zero/Desktop/master_study
grep -A 10 'kdtree_data\.py' docs/superpowers/reports/2026-06-06-script-runnability-report.md | head -15
echo "---"
grep -A 10 'smote_label\.py' docs/superpowers/reports/2026-06-06-script-runnability-report.md | head -15
echo "---"
grep -A 10 'verify_model\.py' docs/superpowers/reports/2026-06-06-script-runnability-report.md | head -15
```

Expected: 三个脚本都有正确的错误类型、行号、修复提示

> **为什么不用 `bp_algorithm`**：bp_algorithm 在旧 JSON 里没数据（17:12 5 条没包含），会显示 "not-run"。改用 `smote_label`（必有数据，缺失 `imblearn` 必失败）。

---

## Task 4: 准备 commit（不执行）

**Files:**
- Stage (do NOT commit):
  - `tools/run_analysis.py` (修改)
  - `tools/generate_runnability_report.py` (新建)
  - `docs/superpowers/reports/run_results-sleep_stage.json` (新生成)
  - `docs/superpowers/reports/2026-06-06-script-runnability-report.md` (新生成)
  - `docs/superpowers/specs/2026-06-06-script-runnability-design.md` (本计划)
  - `docs/superpowers/plans/2026-06-06-script-runnability-plan.md` (本计划)

### Step 4.1: 预览变更

Run:
```bash
cd /Users/zero/Desktop/master_study
git status
```

Expected: 看到上面 6 个文件的 untracked 或 modified 状态

### Step 4.2: 准备 git add 命令（不执行）

**不要执行以下命令**，只是准备：

```bash
cd /Users/zero/Desktop/master_study
git add tools/run_analysis.py \
        tools/generate_runnability_report.py \
        docs/superpowers/reports/run_results-sleep_stage.json \
        docs/superpowers/reports/2026-06-06-script-runnability-report.md \
        docs/superpowers/specs/2026-06-06-script-runnability-design.md \
        docs/superpowers/plans/2026-06-06-script-runnability-plan.md

git commit -m "docs: 48 脚本可运行性报告 (29 新跑 + 5 旧 + 14 未跑 + 1 跳过)

- 扩展 tools/run_analysis.py 加 --filter {all,sleep_classify,sleep_stage}、--output、--dry-run、--print-output
- 新建 tools/generate_runnability_report.py：合并 5+29=34 条 run_results + 48 个静态扫描结果
- 报告含功能一句话、失败原因、修复提示、行号、5 级优先级
- 用 rel_path 作 dict key 解决 psg_rnn_lstm / test 同名覆盖
- merge_results 三级回退：rel_path 精确 > 末段文件名 > label
- data_deal/test.py 在磁盘但不在 SCRIPTS_ALL（漏网），报告以 not-run 出现
"
```

**等待用户确认后再执行**。AGENTS.md 明确："不要在没有用户明确要求的情况下 git add/commit/push"。

---

## Self-Review（计划写完后做）

- [x] Spec coverage: 实现/扩展 2 个工具、跑 29 脚本、生成报告、stage 6 文件 — 全部覆盖
- [x] Placeholder scan: 无 "TBD/TODO"，每步都有具体代码
- [x] Type consistency: ScriptInfo 的字段在 merge_results / render_markdown / classify_priority 一致
- [x] Commit 步骤明确标注"不执行，等用户确认"
- [x] 计数自洽：SCRIPTS_ALL=47（旧 18 + 新 29），discover_scripts=48（含 1 漏网 data_deal/test.py），feature_deal 跳过
- [x] 数据源诚实标注：5 旧（17:12 JSON）而非 18 旧（混淆了 markdown 报告里的 18）
- [x] importlib mock 改 subprocess 避开副作用
- [x] python3 → master_study_env/bin/python 统一
- [x] 同名 stem 处理：rel_path 作 key

---

## 产出物汇总

| 文件 | 类型 | 行数估计 |
|------|------|---------|
| `tools/run_analysis.py` | 扩展 | +60 |
| `tools/generate_runnability_report.py` | 新建 | ~280 |
| `docs/superpowers/reports/run_results-sleep_stage.json` | 新生成 | 29 entries |
| `docs/superpowers/reports/2026-06-06-script-runnability-report.md` | 新生成 | ~750 |
| `docs/superpowers/specs/2026-06-06-script-runnability-design.md` | 已有 | (本计划) |
| `docs/superpowers/plans/2026-06-06-script-runnability-plan.md` | 已有 | (本计划) |

## 下一步

提交计划到 `docs/superpowers/plans/2026-06-06-script-runnability-plan.md`，等用户选择 subagent-driven 或 inline execution。
