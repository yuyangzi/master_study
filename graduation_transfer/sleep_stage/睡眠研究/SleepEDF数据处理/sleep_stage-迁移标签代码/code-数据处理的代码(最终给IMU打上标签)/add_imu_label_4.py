import pandas as pd

# 读取文件1（含 start_time, end_time, predicted_label）
label_path = "E:/master_paper_and_project/sleep_stage/time_frequent_signal/label_gjx/time_frequent_label_gjx_0715.csv"
file1 = pd.read_csv(label_path)
# 确保时间列是数字格式（浮点或整数）
# 将 start_time 和 end_time 转为 datetime 对象
file1['start_time'] = pd.to_datetime(file1['start_time'], format='%Y-%m-%d %H:%M:%S.%f')
file1['end_time'] = pd.to_datetime(file1['end_time'], format='%Y-%m-%d %H:%M:%S.%f')

# 转为浮点型时间戳（秒数）
file1['start_ts'] = file1['start_time'].apply(lambda x: x.timestamp())
file1['end_ts'] = file1['end_time'].apply(lambda x: x.timestamp())
print(file1.head())
# 读取文件2（IMU数据），比如：
# timestamp,x,y,z ...
imu_path = "E:/master_paper_and_project/sleep_stage/EEG_data/imu_gjx/imu_gjx_0715.csv"
file2 = pd.read_csv(imu_path)

# 确保时间戳是数字格式
# 格式： '3:48:59.930 2025/3/30' → datetime
file2[['clock', 'date']] = file2['time_stamp'].str.split(' ', expand=True)

# 拼接成完整时间字符串：2025/3/30 03:48:59.930
file2['datetime_str'] = file2['date'] + ' ' + file2['clock']

# 转换为 datetime 对象
file2['datetime'] = pd.to_datetime(file2['datetime_str'], format='%Y/%m/%d %H:%M:%S.%f')

# 转换为浮点时间戳
file2['timestamp'] = file2['datetime'].apply(lambda x: x.timestamp())
print(file2.head())

# 添加 predicted_label 列
file2['predicted_label'] = None
# 匹配标签
for _, row in file1.iterrows():
    mask = (file2['timestamp'] >= row['start_ts']) & (file2['timestamp'] <= row['end_ts'])
    file2.loc[mask, 'predicted_label'] = row['predicted_label']

output_path = "E:/master_paper_and_project/sleep_stage/time_frequent_signal/imu_label_gjx/imu_label_gjx.csv"
# 只保留需要的列
output = file2[['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'predicted_label']]
output = output.dropna(subset=['predicted_label'])
output = output[output['ax'] != 0]
output = output[output['ay'] != 0]
output = output[output['az'] != 0]
output = output[output['gx'] != 0]
output = output[output['gy'] != 0]
output = output[output['gz'] != 0]
output.to_csv(output_path, index=False)

#

