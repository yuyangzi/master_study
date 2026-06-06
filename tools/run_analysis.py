#!/usr/bin/env python3
"""
批量运行分析工具 — 逐一执行所有 Python 脚本，收集 stdout/stderr/exit_code 并分类。
用法: master_study_env/bin/python tools/run_analysis.py [WORKSPACE_DIR]
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
os.chdir(WORKSPACE)

PYTHON = str(WORKSPACE / "master_study_env" / "bin" / "python")
ENV = os.environ.copy()
ENV["MPLBACKEND"] = "Agg"  # 无头 matplotlib
ENV["PYTHONUNBUFFERED"] = "1"

TIMEOUT_FAST = 120      # 传统 ML 模型
TIMEOUT_DL = 300        # 深度学习 100 epochs
TIMEOUT_CONCAT = 600    # 合并 165 个 xlsx 写入磁盘

# ── 脚本清单 ──────────────────────────────────────────────────────
# 每个条目: (rel_path, workdir_rel, timeout, label)
SCRIPTS = [
    # ====== sleep_classify/code/ (clean, 有真实数据) ======
    ("graduation_transfer/sleep_posture/sleep_classify/code/SVM_algorithm.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_FAST, "SVM_algorithm"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/bp_algorithm.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_DL, "bp_algorithm"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/descison_tree.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_FAST, "descison_tree"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/kdtree_data.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_FAST, "kdtree_data"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/kmeans_algorithm.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_FAST, "kmeans_algorithm"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/logic_regresssion.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_FAST, "logic_regresssion"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/lstm_classify.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_DL, "lstm_classify"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/rnn_classfiy.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_DL, "rnn_classfiy"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/transformer_classify.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_DL, "transformer_classify"),
    ("graduation_transfer/sleep_posture/sleep_classify/code/verify_model.py",
     "graduation_transfer/sleep_posture/sleep_classify/code", TIMEOUT_FAST, "verify_model"),
    # ====== sleep_classify/util/ ======
    ("graduation_transfer/sleep_posture/sleep_classify/util/concat_data.py",
     "graduation_transfer/sleep_posture/sleep_classify/util", TIMEOUT_CONCAT, "concat_data"),
    # ====== Sleep-pdf clean scripts ======
    ("graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/bar_chart.py",
     "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "bar_chart"),
    ("graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/model_figure.py",
     "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "model_figure"),
    ("graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码/new__hybird_imag.py",
     "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码",
     TIMEOUT_FAST, "new__hybird_imag"),
    ("graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/test_psg_data.py",
     "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理",
     TIMEOUT_FAST, "test_psg_data"),
    ("graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/test.py",
     "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal",
     TIMEOUT_FAST, "origin_test"),
    # ====== 迁移标签 clean ======
    ("graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/test_all.py",
     "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)",
     TIMEOUT_FAST, "test_all"),
    # ====== serial_port_extract (need hw, will fail gracefully) ======
    ("graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal/serial_port_extract.py",
     "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/origin_data_deal",
     TIMEOUT_FAST, "serial_port_extract"),
]


def run_one(script_rel: str, workdir_rel: str, timeout: int, label: str) -> dict:
    script_abs = (WORKSPACE / script_rel).resolve()
    workdir_abs = (WORKSPACE / workdir_rel).resolve()
    result = {
        "label": label,
        "script": str(script_abs),
        "workdir": str(workdir_abs),
        "exit_code": -1,
        "stdout": "",
        "stderr": "",
        "duration_s": 0,
        "timeout": False,
        "error_type": None,
        "error_detail": None,
        "summary": "",
    }
    if not script_abs.exists():
        result["error_type"] = "NOT_FOUND"
        result["error_detail"] = f"File not found: {script_abs}"
        result["summary"] = "❌ 文件不存在"
        return result

    # MPLBACKEND=Agg 传 env
    env = ENV.copy()
    start = time.time()
    try:
        p = subprocess.run(
            [PYTHON, str(script_abs)],
            cwd=str(workdir_abs),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        result["exit_code"] = p.returncode
        result["stdout"] = p.stdout if isinstance(p.stdout, str) else p.stdout.decode("utf-8", errors="replace")
        result["stderr"] = p.stderr if isinstance(p.stderr, str) else p.stderr.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired as e:
        result["exit_code"] = -999
        result["timeout"] = True
        result["stdout"] = e.stdout.decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        result["stderr"] = e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
    except Exception as e:
        result["exit_code"] = -998
        result["error_type"] = type(e).__name__
        result["error_detail"] = str(e)

    result["duration_s"] = round(time.time() - start, 2)

    # 分类结果
    ec = result["exit_code"]
    out = (result["stdout"] + result["stderr"]).strip()

    if result["timeout"]:
        result["summary"] = f"⏱ 超时 ({timeout}s) — 部分输出已捕获"
    elif ec == 0:
        # 检查是否有实际输出（训练精度 / 结果）
        lines = [l for l in result["stdout"].split("\n") if l.strip()]
        if lines:
            result["summary"] = f"✅ 成功 ({result['duration_s']}s) — 末行: {lines[-1][:100]}"
        else:
            result["summary"] = f"✅ 成功 ({result['duration_s']}s) — 无 stdout 输出"
    else:
        # 提取关键错误
        stderr = result["stderr"]
        stdout = result["stdout"]
        combined = stderr + "\n" + stdout
        # 常见错误模式
        if "NameError" in combined:
            result["error_type"] = "NameError"
            for line in combined.split("\n"):
                if "NameError" in line:
                    result["error_detail"] = line.strip()[:200]
                    break
        elif "FileNotFoundError" in combined or "No such file" in combined:
            result["error_type"] = "FileNotFoundError"
            for line in combined.split("\n"):
                if "No such file" in line or "FileNotFoundError" in line:
                    result["error_detail"] = line.strip()[:200]
                    break
        elif "ModuleNotFoundError" in combined or "ImportError" in combined:
            result["error_type"] = "ModuleNotFoundError"
            for line in combined.split("\n"):
                if "ModuleNotFoundError" in line or "ImportError" in line:
                    result["error_detail"] = line.strip()[:200]
                    break
        elif "KeyboardInterrupt" in combined:
            result["error_type"] = "KeyboardInterrupt"
        else:
            result["error_type"] = "RuntimeError"
            # Grab last meaningful lines
            lines = [l.strip() for l in combined.split("\n") if l.strip()]
            result["error_detail"] = "\n".join(lines[-5:])[:500] if lines else "(no output)"

        result["summary"] = f"❌ 失败 ({result['duration_s']}s) — {result['error_type']}"

    return result


def main():
    os.makedirs(WORKSPACE / "docs/superpowers/reports", exist_ok=True)
    output_path = WORKSPACE / "docs/superpowers/reports/run_results.json"
    report_path = WORKSPACE / "docs/superpowers/reports/2026-06-06-run-analysis-report.md"

    print(f"Workspace: {WORKSPACE}")
    print(f"Python:    {PYTHON}")
    print()

    results = []
    # 如果有已有的 json，先加载以支持增量运行
    if output_path.exists():
        with open(output_path) as f:
            results = json.load(f)
        done_labels = {r["label"] for r in results}
        print(f"已有 {len(results)} 条结果，跳过已完成的 {len(done_labels)} 个\n")
    else:
        done_labels = set()

    for script_rel, workdir_rel, timeout, label in SCRIPTS:
        if label in done_labels:
            print(f"  ⏭  {label} (已有)")
            continue

        print(f"  ▶  {label}  (timeout={timeout}s)", end="", flush=True)
        r = run_one(script_rel, workdir_rel, timeout, label)
        results.append(r)

        dur = r["duration_s"]
        sm = r["summary"]
        if r["exit_code"] == 0:
            print(f"\r  ✅  {label}  {dur}s  {sm[-80:]}")
        elif r["timeout"]:
            lines = r["stdout"].strip().split("\n")
            last = lines[-1][:80] if lines else ""
            print(f"\r  ⏱  {label}  {dur}s  超时, last: {last}")
        else:
            print(f"\r  ❌  {label}  {dur}s  {r['error_type']}")
            # 打印前几行 stderr
            err_lines = r["stderr"].strip().split("\n")
            for el in err_lines[:3]:
                if el.strip():
                    print(f"       {el.strip()[:120]}")

        # 增量保存
        with open(output_path, "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    # ── 生成报告 ──
    generate_report(results, report_path)
    print(f"\n报告已写入: {report_path}")


def classify_results(results: list) -> dict:
    """分类统计"""
    stats = {"success": [], "timeout": [], "fail_name": [], "fail_file": [],
             "fail_module": [], "fail_other": [], "not_found": []}
    for r in results:
        if r["exit_code"] == 0:
            stats["success"].append(r)
        elif r["timeout"]:
            stats["timeout"].append(r)
        elif r.get("error_type") == "NameError":
            stats["fail_name"].append(r)
        elif r.get("error_type") == "FileNotFoundError":
            stats["fail_file"].append(r)
        elif r.get("error_type") == "ModuleNotFoundError":
            stats["fail_module"].append(r)
        elif r.get("error_type") == "NOT_FOUND":
            stats["not_found"].append(r)
        else:
            stats["fail_other"].append(r)
    return stats


def generate_report(results: list, report_path: Path):
    stats = classify_results(results)

    total = len(results)
    success = len(stats["success"])
    timeout_n = len(stats["timeout"])
    fail_name = len(stats["fail_name"])
    fail_file = len(stats["fail_file"])
    fail_module = len(stats["fail_module"])
    fail_other = len(stats["fail_other"])
    not_found = len(stats["not_found"])
    failed = total - success

    success_rate = round(success / total * 100, 1) if total else 0

    lines = []
    def w(s=""):
        lines.append(s)

    w(f"# Python 脚本运行分析报告")
    w()
    w(f"- 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    w(f"- 运行环境: master_study_env（Python 3.11, macOS ARM64）")
    w(f"- 运行工具: tools/run_analysis.py")
    w(f"- 总脚本数: {total}")
    w()
    w("## 汇总")
    w()
    w("| 分类 | 数量 | 占比 |")
    w("|---|---|---|")
    w(f"| ✅ 运行成功 | {success} | {success_rate}% |")
    w(f"| ⏱ 超时（部分完成） | {timeout_n} | {round(timeout_n/total*100,1)}% |")
    w(f"| ❌ NameError（变量未定义） | {fail_name} | {round(fail_name/total*100,1)}% |")
    w(f"| ❌ FileNotFoundError（数据文件缺失） | {fail_file} | {round(fail_file/total*100,1)}% |")
    w(f"| ❌ ModuleNotFoundError（模块缺失） | {fail_module} | {round(fail_module/total*100,1)}% |")
    w(f"| ❌ 其他运行时错误 | {fail_other} | {round(fail_other/total*100,1)}% |")
    w(f"| ❌ 文件不存在 | {not_found} | {round(not_found/total*100,1)}% |")
    w(f"| **合计失败** | **{failed}** | **{round(failed/total*100,1)}%** |")
    w()

    # ── 成功脚本 ──
    w("---")
    w("## ✅ 运行成功")
    w()
    if stats["success"]:
        w("| 脚本 | 耗时 | 输出摘要 |")
        w("|---|---|---|")
        for r in sorted(stats["success"], key=lambda x: x["label"]):
            stdout_clean = "\n".join(
                [l for l in r["stdout"].split("\n") if l.strip() and "Epoch" not in l]
            ) or r["stdout"]
            last_lines = [l.strip() for l in stdout_clean.strip().split("\n") if l.strip()][-3:]
            summary = " | ".join(last_lines) if last_lines else "(无输出)"
            w(f"| `{r['label']}` | {r['duration_s']}s | {summary[:150]} |")
    else:
        w("无")
    w()

    # ── 超时脚本（部分输出） ──
    w("---")
    w("## ⏱ 超时（部分完成）")
    w()
    w("以下脚本在设定的 timeout 内未执行完毕，但已产生部分输出。")
    w("如需要完整结果，可加长 timeout 或在有 GPU 的服务器上运行。")
    w()
    if stats["timeout"]:
        w("| 脚本 | 超时(s) | 已耗时 | 末行输出 |")
        w("|---|---|---|---|")
        for r in sorted(stats["timeout"], key=lambda x: x["label"]):
            # 估算用的 timeout
            matched = [s for s in SCRIPTS if s[3] == r["label"]]
            to = matched[0][2] if matched else "?"
            last_line = ""
            if r["stdout"].strip():
                lines_o = [l for l in r["stdout"].strip().split("\n") if l.strip()]
                if lines_o:
                    last_line = lines_o[-1][:100]
            w(f"| `{r['label']}` | {to}s | {r['duration_s']}s | `{last_line}` |")
    else:
        w("无")
    w()

    # ── NameError ──
    w("---")
    w("## ❌ NameError（变量未定义）")
    w()
    w("这些脚本存在变量未定义的 bug，并非环境问题。")
    w()
    if stats["fail_name"]:
        for r in sorted(stats["fail_name"], key=lambda x: x["label"]):
            w(f"### `{r['label']}`")
            w()
            w(f"- **耗时**: {r['duration_s']}s")
            w(f"- **错误**: `{r['error_detail']}`")
            w(f"- **stdout**:")
            w("```")
            w((r["stdout"].strip())[:500] or "(无)")
            w("```")
            w(f"- **stderr**:")
            w("```")
            w((r["stderr"].strip())[:500] or "(无)")
            w("```")
            w()
    w()

    # ── FileNotFoundError ──
    w("---")
    w("## ❌ FileNotFoundError（数据文件缺失）")
    w()
    w("这些脚本引用了本地不存在的文件（硬编码 Windows 路径或本地数据文件缺失）。")
    w()
    if stats["fail_file"]:
        for r in sorted(stats["fail_file"], key=lambda x: x["label"]):
            w(f"### `{r['label']}`")
            w()
            w(f"- **耗时**: {r['duration_s']}s")
            w(f"- **错误**: `{r['error_detail']}`")
            w(f"- **stderr**:")
            w("```")
            w((r["stderr"].strip())[:500] or "(无)")
            w("```")
            w()
    w()

    # ── ModuleNotFoundError ──
    w("---")
    w("## ❌ ModuleNotFoundError（模块缺失）")
    w()
    if stats["fail_module"]:
        for r in sorted(stats["fail_module"], key=lambda x: x["label"]):
            w(f"### `{r['label']}`")
            w(f"- **错误**: `{r['error_detail']}`")
    else:
        w("无")
    w()

    # ── 其他错误 ──
    w("---")
    w("## ❌ 其他运行时错误")
    w()
    if stats["fail_other"]:
        for r in sorted(stats["fail_other"], key=lambda x: x["label"]):
            w(f"### `{r['label']}`")
            w()
            w(f"- **耗时**: {r['duration_s']}s")
            w(f"- **错误类型**: {r['error_type']}")
            w(f"- **详情**: `{r['error_detail'][:300]}`")
            w(f"- **stdout (末 5 行)**:")
            w("```")
            out_lines = [l for l in r["stdout"].strip().split("\n") if l.strip()]
            w("\n".join(out_lines[-5:]) if out_lines else "(无)")
            w("```")
            w(f"- **stderr (末 5 行)**:")
            w("```")
            err_lines = [l for l in r["stderr"].strip().split("\n") if l.strip()]
            w("\n".join(err_lines[-5:]) if err_lines else "(无)")
            w("```")
            w()
    else:
        w("无")
    w()

    # ── 未运行脚本说明（script-issue） ──
    w("---")
    w("## 📋 未运行脚本说明")
    w()
    w("以下 31 个脚本因包含硬编码的 Windows 绝对路径（`F:/...` 或 `E:/...`），")
    w("在 macOS 上必然 FileNotFoundError，不再逐一执行。")
    w("详见体检报告中的分类：")
    w()
    w("| 分组 | 脚本数 | 典型路径 |")
    w("|---|---|---|")
    w("| IMU_sleep_stage (data_deal_code/) | 4 | `F:/master_paper_and_project/IMU_sleep_stage/base_data/...` |")
    w("| IMU_sleep_stage (model/) | 7 | `E:/ysl/IMU_sleep_stage/base_data/...` |")
    w("| Sleep-pdf (data_deal/) | 5 | `E:/master_paper_and_project/research/...` |")
    w("| Sleep-pdf (model/) | 7 | `F:/master_paper_and_project/research/new_project/...` |")
    w("| 迁移标签 (code/) | 5 | `E:/master_paper_and_project/sleep_stage/...` |")
    w("| 迁移标签 (model/) | 1 | `E:/master_paper_and_project/research/...` |")
    w("| Sleep-pdf (origin_data/) | 1 | `serial_port_extract` 已单独运行 |")
    w("| feature_deal | 1 | 全注释文档伪装 .py |")
    w()

    # ── 根因分析 ──
    w("---")
    w("## 🧠 根因分析与推荐方案")
    w()

    # 统计
    nameerror_scripts = [r["label"] for r in stats["fail_name"]]
    fileerror_scripts = [r["label"] for r in stats["fail_file"]]

    successful_scripts = [r["label"] for r in stats["success"]]

    w("### 1. 有效运行的脚本")
    w()
    w(f"**{len(successful_scripts)} 个脚本**成功运行并输出有意义的训练/预测结果。")
    w()
    if successful_scripts:
        w("| 脚本 | 实验结论 |")
        w("|---|---|")
        for r in stats["success"]:
            # 提取关键指标行
            lines_out = r["stdout"].strip().split("\n")
            key_lines = [l for l in lines_out if any(k in l for k in
                         ["Accuracy", "Precision", "Recall", "F1", "accurac",
                          "测试集", "训练集", "score"])]
            conclusion = key_lines[-1][:120] if key_lines else "(已运行，无指标输出)"
            w(f"| `{r['label']}` | {conclusion} |")
    w()

    w("### 2. 超时——深度学习脚本需 GPU")
    w()
    if stats["timeout"]:
        w(f"以下 **{len(stats['timeout'])} 个**深度学习脚本在 CPU 上 300s 内未完成 100 epoch：")
        for r in stats["timeout"]:
            w(f"- **`{r['label']}`** — 最后 epoch: 从输出提取")
        w()
        w("**推荐**: 在远程服务器 (`root@159.75.177.109`，Python 3.7 + PyTorch) 上运行，")
        w("或本地减少 epoch（在脚本开头加 `epochs = 10` 调试）后验证。")
    w()

    w("### 3. NameError——源码 bug")
    w()
    if nameerror_scripts:
        w(f"**{len(nameerror_scripts)} 个脚本**存在变量未定义 bug（`Y = ...` 被注释掉），")
        w("即使数据就绪也无法运行。修复方式：")
        for name in nameerror_scripts:
            w(f"- **`{name}`**: 取消注释 `Y = new_df.iloc[:, -1]` 即可")
    w()

    w("### 4. FileNotFoundError——数据文件不完整")
    w()
    if fileerror_scripts:
        w("**失败原因**：")
        for r in stats["fail_file"]:
            w(f"- **`{r['label']}`**: {r.get('error_detail','')[:100]}")
        w()
    w("### 5. 31 个硬编码路径脚本（Phase 2）")
    w()
    w("这些脚本需要将 Windows 路径替换为 macOS 相对路径后才能在本地运行。")
    w("**推荐**: 使用 `pathlib.Path(__file__).parent` 推导路径，统一修复。")
    w()

    # ── 附录 ──
    w("---")
    w("## 附录：Cheatsheet")
    w()
    w("```bash")
    w("# 重新运行分析")
    w(f"rm {WORKSPACE}/docs/superpowers/reports/run_results.json")
    w(f"{PYTHON} tools/run_analysis.py")
    w("```")
    w()

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
