import pandas as pd
import numpy as np
import os
import random
from datetime import datetime
from pathlib import Path

def load_imu_data(csv_path):
    """
    加载IMU睡眠阶段数据
    
    Args:
        csv_path (str): CSV文件路径
    
    Returns:
        pd.DataFrame: 加载的数据
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"数据加载成功。数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"数据加载错误: {e}")
        return None

def validate_data(df):
    """
    验证数据格式
    
    Args:
        df (pd.DataFrame): 输入数据框
    
    Returns:
        bool: 数据是否有效
    """
    # 检查必要的列
    required_columns = ['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'predicted_label']
    
    # 如果列名不匹配，检查是否有predict_label而不是predicted_label
    if 'predict_label' in df.columns:
        df = df.rename(columns={'predict_label': 'predicted_label'})
        print("将列名 'predict_label' 重命名为 'predicted_label'")
    
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        print(f"缺少必要的列: {missing_cols}")
        print(f"实际列: {list(df.columns)}")
        return False, df
    
    # 检查标签值
    unique_labels = df['predicted_label'].unique()
    expected_labels = {0, 1, 2, 3}
    
    if not set(unique_labels).issubset(expected_labels):
        print(f"警告: 发现意外的标签值: {unique_labels}")
        print(f"期望标签: {expected_labels}")
    
    print(f"数据验证通过。标签分布:")
    print(df['predicted_label'].value_counts().sort_index())
    
    return True, df

def find_continuous_segments(df, segment_length=7000):
    """
    查找每个睡眠阶段的连续数据段
    
    Args:
        df (pd.DataFrame): 输入数据框
        segment_length (int): 需要的连续数据长度
    
    Returns:
        dict: 每个标签的连续段起始位置列表
    """
    segments = {0: [], 1: [], 2: [], 3: []}
    
    for label in segments.keys():
        # 找到所有属于该标签的位置
        label_indices = df[df['predicted_label'] == label].index.tolist()
        
        if len(label_indices) < segment_length:
            print(f"警告: 标签 {label} 的数据量 {len(label_indices)} 小于所需的 {segment_length}")
            continue
        
        # 查找连续段
        i = 0
        while i < len(label_indices):
            # 开始一个潜在的连续段
            start_idx = i
            
            # 向后查找连续的索引
            while i + 1 < len(label_indices) and label_indices[i + 1] == label_indices[i] + 1:
                i += 1
            
            end_idx = i
            segment_size = end_idx - start_idx + 1
            
            # 如果连续段长度足够，记录可能的起始位置
            if segment_size >= segment_length:
                # 该连续段内可以选择的起始位置
                possible_starts = label_indices[start_idx:end_idx - segment_length + 2]
                segments[label].extend(possible_starts)
            
            i += 1
        
        print(f"标签 {label}: 找到 {len(segments[label])} 个可能的{segment_length}长度连续段起始位置")
    
    return segments

def extract_random_segments(df, segments_dict, segment_length=7000, num_segments_per_label=1):
    """
    从每个睡眠阶段随机抽取连续数据段
    
    Args:
        df (pd.DataFrame): 原始数据
        segments_dict (dict): 连续段位置字典
        segment_length (int): 段长度
        num_segments_per_label (int): 每个标签抽取的段数
    
    Returns:
        list: 抽取的数据段列表
    """
    extracted_segments = []
    
    for label, possible_starts in segments_dict.items():
        if len(possible_starts) == 0:
            print(f"标签 {label}: 没有足够的连续数据段")
            continue
        
        # 随机选择起始位置
        num_to_extract = min(num_segments_per_label, len(possible_starts))
        selected_starts = random.sample(possible_starts, num_to_extract)
        
        for start_pos in selected_starts:
            # 抽取连续段
            segment = df.iloc[start_pos:start_pos + segment_length].copy()
            extracted_segments.append(segment)
            print(f"标签 {label}: 从位置 {start_pos} 抽取了 {segment_length} 条连续数据")
    
    return extracted_segments

def save_segments_to_csv(segments, output_dir):
    """
    将所有抽取的数据段合并保存到一个CSV文件中，使用时间戳命名
    
    Args:
        segments (list): 数据段列表
        output_dir (str): 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if not segments:
        print("没有数据段需要保存")
        return []
    
    # 生成基于当前时间的文件名
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d%H%M")
    filename = f"{timestamp}_data.csv"
    
    # 合并所有数据段
    combined_data = pd.concat(segments, ignore_index=True)
    
    # 保存为单个CSV文件
    filepath = os.path.join(output_dir, filename)
    combined_data.to_csv(filepath, index=False)
    
    print(f"保存合并文件: {filepath}")
    print(f"  - 文件生成时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  - 总数据长度: {len(combined_data)}")
    print(f"  - 包含的睡眠阶段:")
    
    # 统计每个阶段的数量
    label_counts = combined_data['predicted_label'].value_counts().sort_index()
    for label, count in label_counts.items():
        print(f"    阶段 {label}: {count} 条数据")
    
    return [filepath]

def main():
    """
    主函数：执行整个数据处理流程
    """
    # 设置随机种子以确保可重复性
    random.seed(42)
    
    # 文件路径
    csv_path = r"F:\master_paper_and_project\IMU_sleep_stage\base_data\liu_imu_label.csv"
    output_dir = r"F:\master_paper_and_project\IMU_sleep_stage\deal_data_csv"
    
    print("=" * 60)
    print("IMU睡眠阶段数据处理开始")
    print("=" * 60)
    
    # 1. 加载数据
    print("\n1. 加载IMU数据...")
    df = load_imu_data(csv_path)
    if df is None:
        return
    
    # 2. 验证数据
    print("\n2. 验证数据格式...")
    is_valid, df = validate_data(df)
    if not is_valid:
        print("数据验证失败，程序终止")
        return
    
    # 3. 查找连续段
    print("\n3. 查找连续数据段...")
    segments_dict = find_continuous_segments(df, segment_length=7000)
    
    # 4. 随机抽取段
    print("\n4. 随机抽取连续数据段...")
    extracted_segments = extract_random_segments(df, segments_dict, segment_length=7000, num_segments_per_label=1)
    
    # 5. 保存结果
    print("\n5. 保存抽取的数据段...")
    saved_files = save_segments_to_csv(extracted_segments, output_dir)
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("数据处理完成！")
    print(f"共处理了 {len(extracted_segments)} 个数据段")
    print(f"合并后的总数据量: {sum(len(segment) for segment in extracted_segments)} 条")
    print(f"保存位置: {output_dir}")
    print("\n生成的文件:")
    for file in saved_files:
        print(f"  - {os.path.basename(file)}")
    print("=" * 60)
    
    return saved_files

if __name__ == "__main__":
    main()