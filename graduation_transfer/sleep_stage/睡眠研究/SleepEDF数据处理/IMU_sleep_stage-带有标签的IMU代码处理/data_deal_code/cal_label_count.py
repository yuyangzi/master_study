import os
import sys
from typing import Dict
import pandas as pd
from pathlib import Path


def count_labels(input_path: str, label_col: str = 'predicted_label', chunksize: int = 500_000) -> Dict[str, int]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f'输入文件不存在: {input_path}')

    counts: Dict[str, int] = {}

    # 仅读取标签列，减少IO和内存
    for chunk in pd.read_csv(input_path, usecols=[label_col], chunksize=chunksize):
        vc = chunk[label_col].value_counts()
        for k, v in vc.items():
            key = str(k)
            counts[key] = counts.get(key, 0) + int(v)

    return counts


def main():

    input_path = str(Path(__file__).parent.parent / "base_data" / "train_label.csv")
    output_path = str(Path(__file__).parent.parent / "base_data" / "label_count.csv")

    label_col = 'predicted_label'

    counts = count_labels(input_path, label_col=label_col)

    # 打印结果（按数字大小优先排序，否则按字典序）
    def sort_key(x: str):
        try:
            return (0, int(x))
        except ValueError:
            return (1, x)

    print('Label counts:')
    for k in sorted(counts.keys(), key=sort_key):
        print(f'{k}: {counts[k]}')

    # 保存到CSV
    df_out = pd.DataFrame(
        [(k, counts[k]) for k in sorted(counts.keys(), key=sort_key)],
        columns=[label_col, 'count']
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_out.to_csv(output_path, index=False)
    print(f'已保存统计到: {output_path}')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'发生错误: {e}', file=sys.stderr)
        sys.exit(1)