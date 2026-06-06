import matplotlib.pyplot as plt

def read_hex_data_from_txt(file_path):
    data = []
    with open(file_path, 'rb') as file:  # 以二进制模式打开文件
        while True:
            byte_sequence = file.read(15)  # 每次读取 15 字节
            if not byte_sequence:
                break

            hex_values = bytearray(byte_sequence)

            # 查找第一个 0xAA 作为数据包的起始符
            start_index = 0
            while start_index < len(hex_values):
                if hex_values[start_index] == 0xAA:
                    # 检查后续是否有完整的数据包
                    if start_index + 14 <= len(hex_values):
                        if hex_values[start_index + 1] == 0x0C:  # 检查长度标识符
                            acc_x = (hex_values[start_index + 2] << 8) | hex_values[start_index + 3]
                            acc_y = (hex_values[start_index + 4] << 8) | hex_values[start_index + 5]
                            acc_z = (hex_values[start_index + 6] << 8) | hex_values[start_index + 7]
                            gyro_x = (hex_values[start_index + 8] << 8) | hex_values[start_index + 9]
                            gyro_y = (hex_values[start_index + 10] << 8) | hex_values[start_index + 11]
                            gyro_z = (hex_values[start_index + 12] << 8) | hex_values[start_index + 13]

                            data.append(('acc_x', acc_x))
                            data.append(('acc_y', acc_y))
                            data.append(('acc_z', acc_z))
                            data.append(('gyro_x', gyro_x))
                            data.append(('gyro_y', gyro_y))
                            data.append(('gyro_z', gyro_z))

                        # 跳过当前数据包，继续查找下一个可能的起始符
                        break
                start_index += 1  # 继续查找下一个字节

    if not data:
        print(hex_values)  # 打印读取的十六进制值
        print("未找到有效数据包。请检查输入文件或数据格式。")

    return data


def process_and_convert(data):
    acc_x, acc_y, acc_z = [], [], []
    gyro_x, gyro_y, gyro_z = [], [], []

    for d in data:
        if d[0] == 'acc_x':
            acc_value = d[1]
            if acc_value & 0x8000:  # 处理负数
                acc_value = ((~acc_value) & 0xFFFF) + 1
                acc_value = -acc_value
            acc_x.append(acc_value * 0.061 * 0.0098)
        elif d[0] == 'acc_y':
            acc_value = d[1]
            if acc_value & 0x8000:
                acc_value = ((~acc_value) & 0xFFFF) + 1
                acc_value = -acc_value
            acc_y.append(acc_value * 0.061 * 0.0098)
        elif d[0] == 'acc_z':
            acc_value = d[1]
            if acc_value & 0x8000:
                acc_value = ((~acc_value) & 0xFFFF) + 1
                acc_value = -acc_value
            acc_z.append(acc_value * 0.061 * 0.0098)
        elif d[0] == 'gyro_x':
            gyro_value = d[1]
            if gyro_value & 0x8000:
                gyro_value = ((~gyro_value) & 0xFFFF) + 1
                gyro_value = -gyro_value
            gyro_x.append(gyro_value * 8.750 * 0.001)
        elif d[0] == 'gyro_y':
            gyro_value = d[1]
            if gyro_value & 0x8000:
                gyro_value = ((~gyro_value) & 0xFFFF) + 1
                gyro_value = -gyro_value
            gyro_y.append(gyro_value * 8.750 * 0.001)
        elif d[0] == 'gyro_z':
            gyro_value = d[1]
            if gyro_value & 0x8000:
                gyro_value = ((~gyro_value) & 0xFFFF) + 1
                gyro_value = -gyro_value
            gyro_z.append(gyro_value * 8.750 * 0.001)

    return acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z


def plot_data(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, time_interval):
    # 生成时间轴
    time_axis_seconds = [i * time_interval for i in range(len(acc_x))]  # 时间轴为样本索引乘以时间间隔
    time_axis_minutes = [t / 60 for t in time_axis_seconds]  # 转换为分钟

    # 创建图表
    plt.figure(figsize=(12, 10))

    # 加速度图
    plt.subplot(3, 2, 1)
    plt.plot(time_axis_minutes, acc_x, label='Acc X', color='blue')
    plt.title('Acceleration X over Time')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Acceleration (m/s²)')
    plt.legend()

    plt.subplot(3, 2, 2)
    plt.plot(time_axis_minutes, acc_y, label='Acc Y', color='green')
    plt.title('Acceleration Y over Time')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Acceleration (m/s²)')
    plt.legend()

    plt.subplot(3, 2, 3)
    plt.plot(time_axis_minutes, acc_z, label='Acc Z', color='red')
    plt.title('Acceleration Z over Time')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Acceleration (m/s²)')
    plt.legend()

    # 角速度图
    plt.subplot(3, 2, 4)
    plt.plot(time_axis_minutes, gyro_x, label='Gyro X', color='orange')
    plt.title('Gyroscope X over Time')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Gyroscope (degrees/s)')
    plt.legend()

    plt.subplot(3, 2, 5)
    plt.plot(time_axis_minutes, gyro_y, label='Gyro Y', color='purple')
    plt.title('Gyroscope Y over Time')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Gyroscope (degrees/s)')
    plt.legend()

    plt.subplot(3, 2, 6)
    plt.plot(time_axis_minutes, gyro_z, label='Gyro Z', color='brown')
    plt.title('Gyroscope Z over Time')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Gyroscope (degrees/s)')
    plt.legend()

    plt.tight_layout()
    plt.show()


def analyze_data(file_path, start_time=0, end_time=None):
    raw_data = read_hex_data_from_txt(file_path)

    # 处理数据并获取加速度和角速度
    if raw_data:
        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = process_and_convert(raw_data)

        # 选择时间段的数据
        time_interval = 0.008  # 时间间隔为 0.008 s
        start_index = int(start_time * (1 / time_interval))
        end_index = int(end_time * (1 / time_interval)) if end_time else len(acc_x)

        # 确保索引在范围内
        start_index = max(0, start_index)
        end_index = min(len(acc_x), end_index)

        # 切片数据
        acc_x = acc_x[start_index:end_index]
        acc_y = acc_y[start_index:end_index]
        acc_z = acc_z[start_index:end_index]
        gyro_x = gyro_x[start_index:end_index]
        gyro_y = gyro_y[start_index:end_index]
        gyro_z = gyro_z[start_index:end_index]

        plot_data(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, time_interval)
    else:
        print("No valid data found.")

# 调用分析函数
file_path = 'd0000087.txt'  # 请确保这里的路径正确
analyze_data(file_path, start_time=130, end_time=190)  # 选择从 0 到 10 秒的数据进行分析
