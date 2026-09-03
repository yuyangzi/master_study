import os
import sys
import numpy as np
import pandas as pd
from collections import Counter

def choose_downsample_indices_stream(input_path, label_col, target_label, target_count, chunksize, rng):
    # 水库采样，选择保留的标签1的全局行号（相对CSV数据行，而非含表头）
    reservoir = []
    n_seen = 0  # 仅计数目标标签出现次数
    global_row = 0

    for chunk in pd.read_csv(input_path, chunksize=chunksize):
        if label_col not in chunk.columns:
            raise ValueError(f'找不到标签列: {label_col}')
        for _, row in chunk.iterrows():
            is_target = (row[label_col] == target_label)
            if is_target:
                n_seen += 1
                if len(reservoir) < target_count:
                    reservoir.append(global_row)
                else:
                    j = rng.integers(0, n_seen)
                    if j < target_count:
                        reservoir[j] = global_row
            global_row += 1

    return set(reservoir), n_seen  # keep_set, total_target_count


def collect_all_target_indices(input_path, label_col, target_label, chunksize):
    # 收集所有目标标签的全局行号（用于上采样时做有放回抽样并在第三遍输出）
    indices = []
    global_row = 0
    for chunk in pd.read_csv(input_path, chunksize=chunksize):
        if label_col not in chunk.columns:
            raise ValueError(f'找不到标签列: {label_col}')
        vals = (chunk[label_col] == target_label).to_numpy()
        for is_target in vals:
            if is_target:
                indices.append(global_row)
            global_row += 1
    return indices


def write_original_in_order(input_path, output_path, label_col, target_label, keep_set, do_downsample, chunksize):
    # 第二遍：按原顺序写出全部非目标标签；对目标标签：
    # - 下采样：只写 keep_set 中的行
    # - 上采样：写出所有原有目标标签行（保持顺序）
    header_written = False
    global_row = 0

    # 若存在旧文件，先删除
    if os.path.exists(output_path):
        os.remove(output_path)

    for chunk in pd.read_csv(input_path, chunksize=chunksize):
        if label_col not in chunk.columns:
            raise ValueError(f'找不到标签列: {label_col}')

        out_rows = []
        for _, row in chunk.iterrows():
            if row[label_col] == target_label:
                if do_downsample:
                    if global_row in keep_set:
                        out_rows.append(row)
                else:
                    out_rows.append(row)  # 上采样场景：原有的全部保留
            else:
                out_rows.append(row)
            global_row += 1

        if out_rows:
            df_out = pd.DataFrame(out_rows, columns=chunk.columns)
            df_out.to_csv(output_path, index=False, mode='a', header=not header_written)
            header_written = True


def append_upsampled_duplicates(input_path, output_path, label_col, target_label, duplicate_counter, chunksize):
    # 第三遍：按原始顺序，为每个目标标签的全局行号，追加对应的重复次数
    if not duplicate_counter:
        return

    global_row = 0
    for chunk in pd.read_csv(input_path, chunksize=chunksize):
        if label_col not in chunk.columns:
            raise ValueError(f'找不到标签列: {label_col}')

        append_rows = []
        for _, row in chunk.iterrows():
            d = duplicate_counter.get(global_row, 0)
            if d > 0 and row[label_col] == target_label:
                for _ in range(d):
                    append_rows.append(row)
            global_row += 1

        if append_rows:
            df_append = pd.DataFrame(append_rows, columns=chunk.columns)
            df_append.to_csv(output_path, index=False, mode='a', header=False)


def main():
    base_dir = '.'
    input_path = "F:/master_paper_and_project/IMU_sleep_stage/base_data/reasonable_label.csv"
    output_path = "F:/master_paper_and_project/IMU_sleep_stage/base_data/train_label.csv"

    label_col = 'predicted_label'  # 如不同请修改
    target_label = 1
    target_count = 1_500_000
    chunksize = 500_000
    rng = np.random.default_rng(42)

    if not os.path.exists(input_path):
        print(f'输入文件不存在: {input_path}', file=sys.stderr)
        sys.exit(1)

    # 第一遍：确定需保留/追加策略
    keep_set, total_target = choose_downsample_indices_stream(
        input_path, label_col, target_label, target_count, chunksize, rng
    )

    if total_target == 0:
        print('数据中未发现标签1，无法生成目标文件', file=sys.stderr)
        sys.exit(1)

    do_downsample = total_target > target_count

    # 如果需要上采样，准备上采样的重复分配表
    duplicate_counter = {}
    if not do_downsample and total_target < target_count:
        # 收集所有目标标签的全局行号
        all_target_indices = collect_all_target_indices(input_path, label_col, target_label, chunksize)
        # 需要追加的数量
        need = target_count - total_target
        # 有放回从这些全局行号中抽取 need 个，统计每个行号需要重复的次数
        chosen = rng.choice(np.array(all_target_indices), size=need, replace=True)
        duplicate_counter = dict(Counter(chosen.tolist()))

    # 第二遍：按原始顺序写出原始数据
    write_original_in_order(
        input_path, output_path, label_col, target_label, keep_set, do_downsample, chunksize
    )

    # 第三遍（仅上采样）：按原始顺序追加重复的标签1样本到文件末尾
    if not do_downsample and duplicate_counter:
        append_upsampled_duplicates(
            input_path, output_path, label_col, target_label, duplicate_counter, chunksize
        )

    print(f'完成。原标签1数量: {total_target} -> 目标: {target_count}，输出文件: {output_path}')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'发生错误: {e}', file=sys.stderr)
        sys.exit(1)