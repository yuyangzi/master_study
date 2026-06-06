import matplotlib.pyplot as plt

def read_hex_data_from_txt(file_path):
    data = []
    buffer = bytearray()  # 滑动缓冲区
    PACKET_SIZE = 15

    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(256)  # 每次读取较多数据
            if not chunk:
                break
            buffer.extend(chunk)

            # 在缓冲区中查找所有可能的 0xAA 包
            while len(buffer) >= PACKET_SIZE:
                # 找到第一个 0xAA
                try:
                    start_idx = buffer.index(0xAA)
                except ValueError:
                    # 没找到 0xAA，清空缓冲区（或保留最后 N 字节防丢失）
                    break

                # 如果从 start_idx 开始不够一个包，跳出等待更多数据
                if start_idx + PACKET_SIZE > len(buffer):
                    break

                # 检查是否为有效包：AA 后紧跟 0x0C
                if buffer[start_idx + 1] == 0x0C:
                    packet = buffer[start_idx:start_idx + PACKET_SIZE]
                    # 解析数据
                    acc_x = (packet[2] << 8) | packet[3]
                    acc_y = (packet[4] << 8) | packet[5]
                    acc_z = (packet[6] << 8) | packet[7]
                    gyro_x = (packet[8] << 8) | packet[9]
                    gyro_y = (packet[10] << 8) | packet[11]
                    gyro_z = (packet[12] << 8) | packet[13]

                    data.append(('acc_x', acc_x))
                    data.append(('acc_y', acc_y))
                    data.append(('acc_z', acc_z))
                    data.append(('gyro_x', gyro_x))
                    data.append(('gyro_y', gyro_y))
                    data.append(('gyro_z', gyro_z))

                # 移动缓冲区：从 start_idx+1 开始继续查找（允许重叠）
                buffer = buffer[start_idx + 1:]
            # end while (解析 buffer)
        # end while (读文件)
    return data

def process_and_convert(data):
    # 初始化列表
    acc_x, acc_y, acc_z = [], [], []
    gyro_x, gyro_y, gyro_z = [], [], []

    for key, value in data:
        if key == 'acc_x':
            acc_value = value
            if acc_value & 0x8000:  # 16位有符号数
                acc_value = -(0x10000 - acc_value)
            acc_x.append(acc_value * 0.061 * 0.0098)  # 单位：m/s²

        elif key == 'acc_y':
            acc_value = value
            if acc_value & 0x8000:
                acc_value = -(0x10000 - acc_value)
            acc_y.append(acc_value * 0.061 * 0.0098)

        elif key == 'acc_z':
            acc_value = value
            if acc_value & 0x8000:
                acc_value = -(0x10000 - acc_value)
            acc_z.append(acc_value * 0.061 * 0.0098)

        elif key == 'gyro_x':
            gyro_value = value
            if gyro_value & 0x8000:
                gyro_value = -(0x10000 - gyro_value)
            gyro_x.append(gyro_value * 8.750 * 0.001)  # dps

        elif key == 'gyro_y':
            gyro_value = value
            if gyro_value & 0x8000:
                gyro_value = -(0x10000 - gyro_value)
            gyro_y.append(gyro_value * 8.750 * 0.001)

        elif key == 'gyro_z':
            gyro_value = value
            if gyro_value & 0x8000:
                gyro_value = -(0x10000 - gyro_value)
            gyro_z.append(gyro_value * 8.750 * 0.001)

    return acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z

def plot_data(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z):
    n_samples = max(len(acc_x), len(acc_y), len(acc_z), len(gyro_x), len(gyro_y), len(gyro_z))
    if n_samples == 0:
        print("No data to plot.")
        return

    time_interval = 0.008  # 单位：秒（8ms，即约 125Hz）
    time_axis_seconds = [i * time_interval for i in range(n_samples)]
    time_axis_minutes = [t / 60 for t in time_axis_seconds]

    plt.figure(figsize=(14, 10))

    # 加速度
    plt.subplot(3, 2, 1)
    plt.plot(time_axis_minutes, acc_x, color='blue', linewidth=0.8)
    plt.title('Acceleration X')
    plt.xlabel('Time (min)')
    plt.ylabel('Acc X (m/s²)')

    plt.subplot(3, 2, 2)
    plt.plot(time_axis_minutes, acc_y, color='green', linewidth=0.8)
    plt.title('Acceleration Y')
    plt.xlabel('Time (min)')
    plt.ylabel('Acc Y (m/s²)')

    plt.subplot(3, 2, 3)
    plt.plot(time_axis_minutes, acc_z, color='red', linewidth=0.8)
    plt.title('Acceleration Z')
    plt.xlabel('Time (min)')
    plt.ylabel('Acc Z (m/s²)')

    # 角速度
    plt.subplot(3, 2, 4)
    plt.plot(time_axis_minutes, gyro_x, color='orange', linewidth=0.8)
    plt.title('Gyroscope X')
    plt.xlabel('Time (min)')
    plt.ylabel('Gyro X (°/s)')

    plt.subplot(3, 2, 5)
    plt.plot(time_axis_minutes, gyro_y, color='purple', linewidth=0.8)
    plt.title('Gyroscope Y')
    plt.xlabel('Time (min)')
    plt.ylabel('Gyro Y (°/s)')

    plt.subplot(3, 2, 6)
    plt.plot(time_axis_minutes, gyro_z, color='brown', linewidth=0.8)
    plt.title('Gyroscope Z')
    plt.xlabel('Time (min)')
    plt.ylabel('Gyro Z (°/s)')

    plt.tight_layout()
    plt.show()

# 主程序
if __name__ == "__main__":
    file_path = 'd0000003.csv'  # 确保文件存在
    print("Reading and parsing data...")
    raw_data = read_hex_data_from_txt(file_path)

    if raw_data:
        print(f"Successfully parsed {len(raw_data)//6} data packets.")
        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = process_and_convert(raw_data)
        plot_data(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z)
    else:
        print("No valid data found. Please check the file format or content.")