import pandas as pd
import os
from pathlib import Path

def balance_data(input_file, output_dir=None):
    """
    平衡数据集，使每个类别的样本数与最小类别的样本数相同
    
    参数:
        input_file (str): 输入CSV文件路径
        output_dir (str, optional): 输出目录，如果为None则使用输入文件所在目录
    
    返回:
        pd.DataFrame: 平衡后的DataFrame
    """
    # 读取数据
    print(f"正在读取数据: {input_file}")
    df = pd.read_csv(input_file)
    
    # 确保存在label列
    if 'label' not in df.columns:
        raise ValueError("输入文件必须包含'label'列")
    
    # 按label分组并统计每类样本数
    label_counts = df['label'].value_counts().sort_index()
    print("各类别样本数量:")
    print(label_counts)
    
    # 找到最少的样本数
    min_samples = label_counts.min()
    print(f"\n最小样本数: {min_samples}")
    
    # 用于存储平衡后的数据
    balanced_dfs = []
    
    # 对每个类别进行处理
    for label in sorted(df['label'].unique()):
        # 获取当前类别的所有样本
        label_df = df[df['label'] == label].copy()
        
        # 如果当前类别的样本数大于最小样本数，则进行采样
        if len(label_df) > min_samples:
            # 计算需要分成多少段
            num_segments = len(label_df) // min_samples
            
            # 取前min_samples个连续样本
            label_df = label_df.iloc[:min_samples]
            
            print(f"类别 {label}: 从 {len(df[df['label'] == label])} 个样本中选取前 {min_samples} 个连续样本")
        else:
            print(f"类别 {label}: 保持 {len(label_df)} 个样本 (最小类别)")
        
        balanced_dfs.append(label_df)
    
    # 合并所有类别的数据
    balanced_df = pd.concat(balanced_dfs, ignore_index=True)
    
    # # 打乱数据（可选）
    # balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # 保存结果
    if output_dir is None:
        output_dir = os.path.dirname(input_file)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件名
    input_filename = os.path.basename(input_file)
    output_filename = f"balanced_sort_{input_filename}"
    output_path = os.path.join(output_dir, output_filename)
    
    # 保存到CSV
    balanced_df.to_csv(output_path, index=False)
    print(f"\n平衡后的数据已保存到: {output_path}")
    print(f"总样本数: {len(balanced_df)}, 各类别样本数: {balanced_df['label'].value_counts().sort_index().to_dict()}")
    
    return balanced_df

if __name__ == "__main__":
    # 输入文件路径
    input_file = str(Path(__file__).parent.parent / "merge_data" / "2025_09_15_21_data.csv")
    
    # 输出目录
    output_dir = str(Path(__file__).parent.parent / "merge_data")
    
    # 执行数据平衡
    balanced_data = balance_data(input_file, output_dir)
