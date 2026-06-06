# """
# 主要特征数据的处理进行数据融合
# 根据搜索结果，以下是一些可以用于不同睡眠阶段机器学习和预测的特征提取方法：
# 1.功率谱密度（PSD）特征：
# 观察不同睡眠阶段的功率谱密度图，可以看到不同睡眠阶段具有不同的特征。这些特征可以通过mne.time_frequency.psd_welch函数提取
# 。
# 2.时域特征：
# 时域分析法可以提取睡眠特征，捕获睡眠过程中的主要变化，例如信号的均值、方差、标准差、最大值和最小值等
# 。
# 3.频域特征：
# 频域分析法可以提取睡眠特征，例如通过傅里叶变换或功率谱密度（PSD）来提取
# 。
# 4.微分熵特征：
# 可以使用MNE-Python的mne.features.differential_entropy()函数计算微分熵特征，这是一种衡量信号复杂度的特征
# 。
# 5.FFT特征：
# 通过快速傅里叶变换（FFT）从EEG信号中提取特征，可以用于通过机器学习方法提高自动睡眠阶段分类的性能。
# 6.多模态特征：
# 结合EEG和EOG信号，利用多模态特征提取网络，可以提高睡眠阶段分类的准确性。例如，REM和N1阶段的脑电波相似，但EOG波有很大的不同，因此EOG信号对REM和N1期的分类贡献大于EEG信号
# 。
# 7.时频域特征：
# 通过短时傅里叶变换（STFT）或小波变换提取的时频特征，可以提供关于信号频率随时间变化的信息
# 。
# 8.连接性特征：
# 提取不同脑区域之间的功能连接关系，如相干性、相关性等，这些特征可以通过分析不同脑电通道之间的相互作用来获得
# 。
# 9.深度学习特征：
# 深度学习模型能够自动提取数据中的特征并进行预测，例如通过空间图卷积和时间卷积提取睡眠脑电信号的空间特征和时间特征
# 。
# 10.注意力机制特征：
# 采用时空注意机制自动捕获更有价值的时空信息进行高精度分类。
# 这些特征可以用于训练机器学习模型，如随机森林、支持向量机等，进行睡眠阶段的分类和预测。通过结合这些特征，可以提高模型对不同睡眠阶段的识别和预测能力。
# """
# import mne
# import os
# import random
# from datetime import datetime
# import numpy as np
#
# class EdfDataDeal(object):
#
#     def __init__(self, sample_count=10):
#         # 数据集所在的文件夹
#         self.dir_path = "E:/master_paper_and_project/research/all_data/sleep-cassette/"
#         # 每次训练需要获取的用户个数
#         self.sample_count = sample_count
#         # 用于保存的数据位置
#         date_str = datetime.now().strftime("%Y_%m_%d_%H")
#         self.save_path = "E:/master_paper_and_project/research/new_project/merge_data/" + date_str +"_data.fif"
#
#     def deal_all_data(self):
#         # 用于获取所有的数据进行数据分类
#         # 返回的列表中为feature_file:label_file
#         file_list = list()
#         for root, dirs, file_names in os.walk(self.dir_path):
#             for file_name in file_names:
#                 file_list.append(file_name)
#         # 进行排序
#         sort_file_names = sorted(file_list)
#         integrate_file_list = list()
#         for i in range(len(sort_file_names)):
#             if i % 2 == 1:
#                 # 表示为奇数时用于进行数据分类处理
#                 feature_file = sort_file_names[i-1]
#                 label_file = sort_file_names[i]
#                 integrate_file = feature_file + ":" + label_file
#                 integrate_file_list.append(integrate_file)
#
#         # 随机获取20条对应的数据进行返回
#         ret_list = random.sample(integrate_file_list, self.sample_count)
#         return ret_list
#
#     def merge_edf_data_and_label(self):
#         # 主要用于合并edf数据和标
#         # 获取对应整合好的数据列表
#         integrate_file_list = self.deal_all_data()
#         # 对应的edf数据文件
#         psg_files = list()
#         # 对应的edf的标签文件
#         annot_files = list()
#         for integrate_file in integrate_file_list:
#             file_list = integrate_file.split(":")
#             # 特征数据完整路径列表
#             psg_file = self.dir_path + file_list[0]
#             psg_files.append(psg_file)
#             # 标签数据完整路径列表
#             annot_file = self.dir_path + file_list[1]
#             annot_files.append(annot_file)
#
#         # 读取PSG文件和对应的标签文件
#         combined_raw = None
#         combined_annotations = []
#         for psg_file, hypnogram_file in zip(psg_files, annot_files):
#             # 特征的数据
#             psg_raw = mne.io.read_raw_edf(psg_file, preload=True)
#             # 注标签的数据
#             annotations = mne.read_annotations(hypnogram_file)
#
#             if annotations is None:
#                 print(f"Hypnogram 文件 {hypnogram_file} 不包含注释！")
#                 continue
#
#             # 如果是第一个用户的数据，直接初始化 combined_raw
#             if combined_raw is None:
#                 combined_raw = psg_raw
#                 offset = 0  # 第一个文件无时间偏移
#             else:
#                 # 计算时间偏移：拼接数据的最后一个时间点
#                 offset = combined_raw.times[-1] + 1 / combined_raw.info['sfreq']
#                 annotations.onset += offset
#                 combined_raw.append(psg_raw)  # 拼接 PSG 数据
#
#             # 合并注释
#             for onset, duration, description in zip(annotations.onset, annotations.duration,
#                                                     annotations.description):
#                 combined_annotations.append({"onset": onset, "duration": duration, "description": description})
#
#         # 创建新的注释对象
#         final_annotations = mne.Annotations(
#             onset=[ann['onset'] for ann in combined_annotations],
#             duration=[ann['duration'] for ann in combined_annotations],
#             description=[ann['description'] for ann in combined_annotations],
#             orig_time=None
#         )
#
#         # 设置最终注释到拼接后的 PSG 数据中
#         combined_raw.set_annotations(final_annotations)
#
#         # 保存合并后的文件
#         combined_raw.save(self.save_path, overwrite=True)
#
#
# if __name__ == '__main__':
#     EdfDataDeal(sample_count=10).merge_edf_data_and_label()
#
#
