#!/usr/bin/env python3
"""
Replace hardcoded Windows paths (F:/... E:/...) with pathlib.Path(__file__).parent relative paths.
Safe idempotent transform — only modifies lines containing F:/... or E:/... patterns.
"""
import ast
import re
import sys
from pathlib import Path

WORKSPACE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

# ── mapping: script_path → [(old_string, new_expression_or_path)] ──
# new_expression_or_path is either:
#   - a tuple (add_import, path_expression)
#   - or None to skip
#
# path_expression uses 'BASE' as Path(__file__).parent, 'BASE2' for .parent.parent etc.

TRANSFORMS = {}

def rel(base: Path, target: str) -> Path:
    """Compute relative path from base script dir to target path."""
    # Normalize the hardcoded path: replace \ with /, strip drive letter, strip r-prefix
    norm = target.strip().lstrip("rR").strip("\"'")
    norm = norm.replace("\\", "/")
    # Remove drive letter
    if ":" in norm:
        norm = norm.split(":", 1)[1]
    norm = norm.lstrip("/")
    # Build full path if needed — but the hardcoded path is not a local path,
    # it's a Windows path. We need to compute the relative path based on
    # our knowledge of the project structure.
    # This function is NOT used directly — instead we use the mapping below.
    return Path(norm)


def register_transforms():
    W = WORKSPACE

    # ═══════════════════════════════════════════
    # Group A: IMU/data_deal_code/ → ../base_data/
    # Script dir: .../IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code/
    # Data:       .../IMU_sleep_stage-带有标签的IMU代码处理/base_data/
    # ═══════════════════════════════════════════
    IMU_CODE = "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/data_deal_code"
    BASE2 = 'Path(__file__).parent.parent / "base_data"'

    TRANSFORMS[f"{IMU_CODE}/train_data_deal.py"] = [
        ('"F:/master_paper_and_project/IMU_sleep_stage/base_data/reasonable_label.csv"',
         f'str({BASE2} / "reasonable_label.csv")'),
        ('"F:/master_paper_and_project/IMU_sleep_stage/base_data/train_label.csv"',
         f'str({BASE2} / "train_label.csv")'),
    ]
    TRANSFORMS[f"{IMU_CODE}/cal_label_count.py"] = [
        ('"F:/master_paper_and_project/IMU_sleep_stage/base_data/train_label.csv"',
         f'str({BASE2} / "train_label.csv")'),
        ('"F:/master_paper_and_project/IMU_sleep_stage/base_data/label_count.csv"',
         f'str({BASE2} / "label_count.csv")'),
    ]
    TRANSFORMS[f"{IMU_CODE}/smote_label.py"] = [
        ('"F:/master_paper_and_project/IMU_sleep_stage/base_data/liu_imu_label.csv"',
         f'str({BASE2} / "liu_imu_label.csv")'),
        ('"F:/master_paper_and_project/IMU_sleep_stage/base_data/liu_imu_label_smote_label0_100k.csv"',
         f'str({BASE2} / "liu_imu_label_smote_label0_100k.csv")'),
    ]
    # data_deal.py uses raw strings r"F:\..."
    TRANSFORMS[f"{IMU_CODE}/data_deal.py"] = [
        ('r"F:\\master_paper_and_project\\IMU_sleep_stage\\base_data\\liu_imu_label.csv"',
         f'str({BASE2} / "liu_imu_label.csv")'),
        ('r"F:\\master_paper_and_project\\IMU_sleep_stage\\deal_data_csv"',
         f'str({BASE2} / ".." / "deal_data_csv")'),
    ]

    # ═══════════════════════════════════════════
    # Group B: IMU/model/ → ../base_data/
    # Script dir: .../IMU_sleep_stage-带有标签的IMU代码处理/model/
    # Data:       .../IMU_sleep_stage-带有标签的IMU代码处理/base_data/
    # ═══════════════════════════════════════════
    IMU_MODEL = "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/IMU_sleep_stage-带有标签的IMU代码处理/model"
    BASE2_MODEL = 'Path(__file__).parent.parent / "base_data"'

    for fname, old_path, fname_csv in [
        ("imu_kdtree.py",   '"F:/master_paper_and_project/IMU_sleep_stage/base_data/train_label.csv"', "train_label.csv"),
        ("imu_lstm.py",     '"F:/ysl/IMU_sleep_stage/base_data/train_label.csv"', "train_label.csv"),
        ("imu_lstm_rnn.py", '"F:/ysl/IMU_sleep_stage/base_data/train_label.csv"', "train_label.csv"),
        ("imu_cnn.py",      '"E:/ysl/IMU_sleep_stage/base_data/train_label.csv"', "train_label.csv"),
        ("imu_rnn.py",      '"E:/ysl/IMU_sleep_stage/base_data/train_label.csv"', "train_label.csv"),
        ("imu_cnn_rnn.py",  '"E:/ysl/IMU_sleep_stage/base_data/train_label.csv"', "train_label.csv"),
        ("imu_cnn_lstm.py", '"E:/ysl/IMU_sleep_stage/base_data/train_label.csv"', "train_label.csv"),
    ]:
        TRANSFORMS[f"{IMU_MODEL}/{fname}"] = [
            (old_path, f'str({BASE2_MODEL} / "{fname_csv}")'),
        ]

    # ═══════════════════════════════════════════
    # Group C: Sleep-pdf/model/ → ../../merge_data/
    # Script dir: .../Sleep-pdf处理代码/new_project/model-模型训练代码/
    # Data:       .../Sleep-pdf处理代码/new_project/merge_data/
    # ═══════════════════════════════════════════
    PDF_MODEL = "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/model-模型训练代码"
    BASE2_PDF = 'Path(__file__).parent.parent / "merge_data"'

    TRANSFORMS[f"{PDF_MODEL}/psg_lstm.py"] = [
        ('"F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"',
         f'str({BASE2_PDF} / "balanced_sort_2025_09_15_21_data.csv")'),
    ]
    TRANSFORMS[f"{PDF_MODEL}/psg_cnn.py"] = [
        ('"F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"',
         f'str({BASE2_PDF} / "balanced_sort_2025_09_15_21_data.csv")'),
    ]
    TRANSFORMS[f"{PDF_MODEL}/basic_rnn.py"] = [
        ('"F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"',
         f'str({BASE2_PDF} / "balanced_sort_2025_09_15_21_data.csv")'),
    ]
    TRANSFORMS[f"{PDF_MODEL}/hybird_matrix.py"] = [
        ('"F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"',
         f'str({BASE2_PDF} / "balanced_sort_2025_09_15_21_data.csv")'),
    ]
    TRANSFORMS[f"{PDF_MODEL}/psg_rnn_lstm.py"] = [
        ('"F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"',
         f'str({BASE2_PDF} / "balanced_sort_2025_09_15_21_data.csv")'),
    ]

    # These use self.dir_path in class __init__
    for fname, old_path in [
        ("psg_kdtree.py",  '"E:/master_paper_and_project/research/new_project/merge_data/2025_01_14_16_data.csv"'),
        ("psg_knn.py",     '"F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"'),
        ("decsion_tree.py",'"F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"'),
    ]:
        csv_name = old_path.split("/")[-1].rstrip('"')
        TRANSFORMS[f"{PDF_MODEL}/{fname}"] = [
            (old_path, f'str({BASE2_PDF} / "{csv_name}")'),
        ]

    # ═══════════════════════════════════════════
    # Group D: Sleep-pdf/data_deal/ → ../../merge_data/  or  missing data
    # Script dir: .../Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理/
    # ═══════════════════════════════════════════
    PDF_DATA = "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/Sleep-pdf处理代码/new_project/data_deal-sleep-pdf原始数据处理"
    BASE2_DD = 'Path(__file__).parent.parent / "merge_data"'

    TRANSFORMS[f"{PDF_DATA}/balance_data-提取后数据的预处理.py"] = [
        ('r"E:\\master_paper_and_project\\research\\new_project\\merge_data\\2025_09_15_21_data.csv"',
         f'str({BASE2_DD} / "2025_09_15_21_data.csv")'),
        ('r"E:\\master_paper_and_project\\research\\new_project\\merge_data"',
         f'str({BASE2_DD})'),
    ]

    # sleep-cassette / raw_data paths — missing data, but still convert for consistency
    BASE2_RAW = 'Path(__file__).parent.parent.parent.parent / "all_data" / "sleep-cassette"'
    BASE2_NEWRAW = 'Path(__file__).parent.parent / "raw_data"'

    TRANSFORMS[f"{PDF_DATA}/new_feature_deal-EEG提取.py"] = [
        ('"E:/master_paper_and_project/research/all_data/sleep-cassette/"',
         f'str({BASE2_RAW} / "")'),
        ('"E:/master_paper_and_project/research/new_project/merge_data/"',
         f'str({BASE2_DD} / "")'),
    ]
    TRANSFORMS[f"{PDF_DATA}/raw_data_extract.py"] = [
        ('"E:/master_paper_and_project/research/new_project/raw_data/ecg_chy1.xls"',
         f'str({BASE2_NEWRAW} / "ecg_chy1.xls")'),
    ]
    TRANSFORMS[f"{PDF_DATA}/test.py"] = [
        ('"E:/master_paper_and_project/research/all_data/sleep-cassette/SC4001E0-PSG.edf"',
         f'str({BASE2_RAW} / "SC4001E0-PSG.edf")'),
        ('"E:/master_paper_and_project/research/all_data/sleep-cassette/SC4001EC-Hypnogram.edf"',
         f'str({BASE2_RAW} / "SC4001EC-Hypnogram.edf")'),
    ]
    # test.py has 4 occurrences — the last two on lines 69/71 are same as 9/26
    TRANSFORMS[f"{PDF_DATA}/test.py"].append(
        ('"E:/master_paper_and_project/research/all_data/sleep-cassette/SC4001E0-PSG.edf"',
         f'str({BASE2_RAW} / "SC4001E0-PSG.edf")'),
    )
    TRANSFORMS[f"{PDF_DATA}/test.py"].append(
        ('"E:/master_paper_and_project/research/all_data/sleep-cassette/SC4001EC-Hypnogram.edf"',
         f'str({BASE2_RAW} / "SC4001EC-Hypnogram.edf")'),
    )

    # ═══════════════════════════════════════════
    # Group E: 迁移标签/code/ → ../../xxx/
    # Script dir: .../sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)/
    # Data:       .../sleep_stage-迁移标签代码/{model,EEG_data,PSG_deal_data,IMU_deal_data,rawdata,time_frequent_signal}/
    # ═══════════════════════════════════════════
    TAG_CODE = "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/code-数据处理的代码(最终给IMU打上标签)"
    BASE3 = 'Path(__file__).parent.parent'  # → sleep_stage-迁移标签代码/

    TRANSFORMS[f"{TAG_CODE}/eeg_data_add_label_3.py"] = [
        ('"E:/master_paper_and_project/sleep_stage/time_frequent_signal/gjx/"',
         f'str({BASE3} / "time_frequent_signal" / "gjx" / "")'),
        ('"E:/master_paper_and_project/sleep_stage/time_frequent_signal/label_gjx/"',
         f'str({BASE3} / "time_frequent_signal" / "label_gjx" / "")'),
    ]
    TRANSFORMS[f"{TAG_CODE}/eeg_data_deal_1.py"] = [
        ('"E:/master_paper_and_project/sleep_stage/rawdata/gjx/"',
         f'str({BASE3} / "rawdata" / "gjx" / "")'),
        ('"E:/master_paper_and_project/sleep_stage/EEG_data/gjx/"',
         f'str({BASE3} / "EEG_data" / "gjx" / "")'),
    ]
    TRANSFORMS[f"{TAG_CODE}/imu_data_deal_1.py"] = [
        ('"E:/master_paper_and_project/sleep_stage/rawdata/gjx/"',
         f'str({BASE3} / "rawdata" / "gjx" / "")'),
        ('"E:/master_paper_and_project/sleep_stage/EEG_data/imu_gjx/"',
         f'str({BASE3} / "EEG_data" / "imu_gjx" / "")'),
    ]
    TRANSFORMS[f"{TAG_CODE}/eeg_data_to_base_2.py"] = [
        ('"E:/master_paper_and_project/sleep_stage/EEG_data/gjx/"',
         f'str({BASE3} / "EEG_data" / "gjx" / "")'),
        ('"E:/master_paper_and_project/sleep_stage/time_frequent_signal/gjx/"',
         f'str({BASE3} / "time_frequent_signal" / "gjx" / "")'),
    ]
    TRANSFORMS[f"{TAG_CODE}/add_imu_label_4.py"] = [
        ('"E:/master_paper_and_project/sleep_stage/time_frequent_signal/label_gjx/time_frequent_label_gjx_0715.csv"',
         f'str({BASE3} / "time_frequent_signal" / "label_gjx" / "time_frequent_label_gjx_0715.csv")'),
        ('"E:/master_paper_and_project/sleep_stage/EEG_data/imu_gjx/imu_gjx_0715.csv"',
         f'str({BASE3} / "EEG_data" / "imu_gjx" / "imu_gjx_0715.csv")'),
        ('"E:/master_paper_and_project/sleep_stage/time_frequent_signal/imu_label_gjx/imu_label_gjx.csv"',
         f'str({BASE3} / "time_frequent_signal" / "imu_label_gjx" / "imu_label_gjx.csv")'),
    ]
    TRANSFORMS[f"{TAG_CODE}/integrate_deal_process-只看这个代码.py"] = [
        ('"F:/master_paper_and_project/sleep_stage/model/rnn_lstm/best_model_epoch36.pth"',
         f'str({BASE3} / "model" / "rnn_lstm" / "best_model_epoch36.pth")'),
        ('"F:/master_paper_and_project/sleep_stage/EEG_data/complete_path/"',
         f'str({BASE3} / "EEG_data" / "complete_path" / "")'),
        ('"F:/master_paper_and_project/sleep_stage/PSG_deal_data/deal_data/"',
         f'str({BASE3} / "PSG_deal_data" / "deal_data" / "")'),
        ('"F:/master_paper_and_project/sleep_stage/PSG_deal_data/label_data/"',
         f'str({BASE3} / "PSG_deal_data" / "label_data" / "")'),
        ('"F:/master_paper_and_project/sleep_stage/PSG_deal_data/frequent_date_data/"',
         f'str({BASE3} / "PSG_deal_data" / "frequent_date_data" / "")'),
        ('"F:/master_paper_and_project/sleep_stage/IMU_deal_data/deal_data/"',
         f'str({BASE3} / "IMU_deal_data" / "deal_data" / "")'),
        ('"F:/master_paper_and_project/sleep_stage/IMU_deal_data/label_data/"',
         f'str({BASE3} / "IMU_deal_data" / "label_data" / "")'),
    ]

    # ═══════════════════════════════════════════
    # Group F: 迁移标签/model/ → ../../../Sleep-pdf处理代码/new_project/merge_data/
    # Script dir: .../sleep_stage-迁移标签代码/model/
    # Data:       .../Sleep-pdf处理代码/new_project/merge_data/
    # ═══════════════════════════════════════════
    TAG_MODEL = "graduation_transfer/sleep_stage/睡眠研究/SleepEDF数据处理/sleep_stage-迁移标签代码/model"
    BASE5 = 'Path(__file__).parent.parent.parent / "Sleep-pdf处理代码" / "new_project" / "merge_data"'  # 3×parent → SleepEDF数据处理/

    TRANSFORMS[f"{TAG_MODEL}/psg_rnn_lstm.py"] = [
        ('"E:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"',
         f'str({BASE5} / "balanced_sort_2025_09_15_21_data.csv")'),
    ]


def needs_pathlib_import(filepath: Path, content: str) -> bool:
    """Check if file already imports pathlib."""
    if not content:
        return False
    # Already has the import
    if re.search(r'^from pathlib import Path', content, re.MULTILINE):
        return False
    if re.search(r'^import pathlib', content, re.MULTILINE):
        return False
    return True


def ensure_pathlib_import(content: str) -> str:
    """Add 'from pathlib import Path' after existing imports."""
    if re.search(r'^from pathlib import Path', content, re.MULTILINE):
        return content
    # Find last import line
    lines = content.split('\n')
    last_import = -1
    for i, line in enumerate(lines):
        if re.match(r'^(import |from )', line):
            last_import = i
    if last_import >= 0:
        lines.insert(last_import + 1, 'from pathlib import Path')
    else:
        # No existing imports, add after docstring/comment
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('"') and not line.startswith("'") and not line.startswith('#'):
                lines.insert(i, 'from pathlib import Path\n')
                break
        else:
            lines.append('from pathlib import Path')
    return '\n'.join(lines)


def transform_file(rel_path: str, transforms: list) -> int:
    """Apply transforms to a file. Returns number of replacements made."""
    filepath = WORKSPACE / rel_path
    orig = filepath.read_text(encoding='utf-8')
    content = orig
    replacements = 0

    for old_str, new_expr in transforms:
        count = content.count(old_str)
        if count == 0:
            print(f"  ⚠  Pattern not found in {rel_path}: {old_str[:60]}...")
            continue
        content = content.replace(old_str, new_expr)
        replacements += count
        print(f"  ✓  {rel_path}: {count}x replacement — {old_str[:60]}...")

    if replacements == 0:
        return 0

    # Add pathlib import if needed
    if needs_pathlib_import(filepath, content):
        content = ensure_pathlib_import(content)
        print(f"  ➕  {rel_path}: added 'from pathlib import Path'")

    # Validate syntax with ast.parse
    try:
        ast.parse(content)
    except SyntaxError as e:
        print(f"  ❌  SYNTAX ERROR in {rel_path}: {e}")
        print(f"     Reverting changes for this file.")
        filepath.write_text(orig, encoding='utf-8')
        return 0

    filepath.write_text(content, encoding='utf-8')
    return replacements


def main():
    register_transforms()

    total_replacements = 0
    total_files = 0
    skipped = []

    for rel_path, transforms in sorted(TRANSFORMS.items()):
        filepath = WORKSPACE / rel_path
        if not filepath.exists():
            skipped.append((rel_path, "file not found"))
            continue
        n = transform_file(rel_path, transforms)
        if n > 0:
            total_files += 1
            total_replacements += n
        else:
            skipped.append((rel_path, "no changes"))

    print(f"\n{'='*60}")
    print(f"完成: {total_files} 个文件, {total_replacements} 处替换")
    if skipped:
        print(f"跳过: {len(skipped)} 个")
        for f, reason in skipped:
            print(f"  - {f}: {reason}")


if __name__ == "__main__":
    main()
