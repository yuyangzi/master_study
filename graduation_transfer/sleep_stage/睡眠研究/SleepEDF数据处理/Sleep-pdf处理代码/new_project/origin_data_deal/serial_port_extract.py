import serial
import time
import json
def main():
    try:
        ser = serial.Serial(
            port='COM5',
            baudrate=460800,
            timeout=10
        )
        print("串口已打开")

        while True:
            if ser.in_waiting >= 15:  # 假设数据包长度固定
                raw_data = ser.read(15)
                # print(raw_data)
                hex_str = ' '.join(f"{byte:02X}" for byte in raw_data)
                print(hex_str)
                # try:
                #     # parsed = json.loads(raw_data.decode('utf-8'))
                #     # print(f"结构化数据: {parsed}")
                # except Exception as e:
                #     print(f"解析失败: {e}")
            time.sleep(0.1)

    except Exception as e:
        print(f"错误: {e}")
    finally:
        if 'ser' in locals():
            ser.close()


if __name__ == "__main__":
    main()