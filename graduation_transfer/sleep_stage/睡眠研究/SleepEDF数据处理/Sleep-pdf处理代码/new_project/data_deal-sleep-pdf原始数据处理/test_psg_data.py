import mne
# import numpy as np
# import pandas as pd
# import os
# import random
# from scipy.signal import welch
# from datetime import datetime


def extract_data():
    psg_file = "./psg_test.edf"
    raw_psg = mne.io.read_raw_edf(psg_file, preload=True)
    # 获取采样率和通道数据
    sampling_rate = raw_psg.info['sfreq']  # 采样率（单位：Hz）
    print(f"sampling_rate:{sampling_rate}")
    # 提取 EEG Fpz-Cz 通道数据
    print(f"raw_psg.ch_names:{raw_psg.ch_names}")
    if "ECG" in raw_psg.ch_names:
        eeg_data = raw_psg.copy().pick_channels(["ECG"]).get_data()[0]  # (samples,)
        print(f"ECG:{eeg_data}")
    else:
        raise ValueError("Channel 'EEG Fpz-Cz' not found in PSG.edf")


if __name__ == "__main__":
    extract_data()