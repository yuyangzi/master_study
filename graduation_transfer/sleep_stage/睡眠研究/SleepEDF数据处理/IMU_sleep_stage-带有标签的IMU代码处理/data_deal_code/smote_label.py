import os
import pandas as pd
from pathlib import Path

try:
    from imblearn.over_sampling import SMOTE
    _HAS_SMOTE = True
except ImportError:
    SMOTE = None
    _HAS_SMOTE = False

def main():
    input_path = str(Path(__file__).parent.parent / "base_data" / "liu_imu_label.csv")
    output_path = str(Path(__file__).parent.parent / "base_data" / "liu_imu_label_smote_label0_100k.csv")

    df = pd.read_csv(input_path)
    if 'predicted_label' not in df.columns:
        raise ValueError('predicted_label 列不存在')

    X_cols = [c for c in df.columns if c != 'predicted_label']
    df = df.dropna(subset=X_cols + ['predicted_label'])

    y = df['predicted_label'].astype(int)
    X = df[X_cols]

    target_count = 100000
    if not _HAS_SMOTE:
        raise ImportError(
            "缺少依赖: imbalanced-learn。运行: pip install imbalanced-learn"
        )
    smote = SMOTE(random_state=42, sampling_strategy={0: target_count})
    X_res, y_res = smote.fit_resample(X, y)

    df_res = pd.DataFrame(X_res, columns=X_cols)
    df_res['predicted_label'] = y_res

    df_res = df_res.sample(frac=1.0, random_state=42).reset_index(drop=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_res.to_csv(output_path, index=False)

if __name__ == '__main__':
    main()