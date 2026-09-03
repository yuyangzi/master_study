# IoT-63850-2026 论文修改方案（grill-me 决策汇总）

**日期:** 2026-09-04
**稿件:** A Sleep Monitoring Belt–Based Sleep Staging Method via EEG-Guided Label Transfer and Deep Learning
**决定:** Reject & Resubmit（IEEE IoT-J，按新投稿走，cover letter 与 Author Comments 注明原稿号 IoT-63850-2026）
**硬性要求:** Track Changes 标出全部改动；单独提交逐条 response letter；所有图表重新生成并脚本直出。

---

## 〇、审计结论（修改的出发点）

对本地代码的审计确认：**本地代码即论文代码，原数字产生于泄漏评估口径**。证据：

| 事实 | 位置 |
|---|---|
| 无任何 subject 级切分/交叉验证，单次 80/20 随机切 | `psg_rnn_lstm.py:63-68`（random_split）、`psg_lstm.py:26` 等 |
| 10-epoch 滑窗致 train/test 重叠 90% 样本 | `psg_rnn_lstm.py:41-45` |
| 训练 CSV 无 subject/record 列 | `merge_data/*.csv` |
| scaler 全量 fit（含测试集） | `psg_rnn_lstm.py:55-56` 等 |
| 欠采样取每类头部连续段（系统性偏差），shuffle 被注释 | `balance_data-提取后数据的预处理.py:42-47,58-59` |
| 论文混淆矩阵为手填数字绘图 | `new__hybird_imag.py:10-15` |
| 98.64% 硬编码于绘图脚本；checkpoint 实测 99.07%（泄漏口径）；89.77% 无出处 | `bar_chart.py:36` |
| 目标域训练数据实为 liu 一人（4.1M 行 125Hz 采样点，行级随机切） | `train_data_deal.py:104-105`、`imu_cnn_rnn.py:43-45` |
| IMU 标签为模型自预测伪标签，推理端重 fit scaler | `integrate_deal_process-只看这个代码.py:302-304` |

**诚信红线（贯穿全流程）：**
1. 一切数字来自新管线运行输出，**禁止手填图表**，所有图/表/指标必须可从脚本+日志复现，模型权重与日志存档。
2. 论文中的人数、样本数、协议描述与实际运行**逐项一致**（"5-fold CV"等与代码不符的表述全部纠正）。
3. 结果下降是可预期且可辩护的；虚高不可辩护。

---

## 一、十项决策

### D1 修改路线 = 全部重做
以 subject-wise 严格协议重建源域与目标域实验，新数字写入论文。不走"仅文字澄清"路线。

### D2 被试数：真实 N=10（7 存量 + 补采 3）
- 现有完整成对数据 7 人：chy、fnk、gjx、hgx、hyh、zj、liu（liu 6 夜，chy 2-3 夜，其余 1 夜）。
- 补采 3 名健康年轻志愿者（与 D7 相关），凑成真实 N=10，论文方可写 10 人。
- **条件:** ① 全部目标域结果（LOSO/κ/混淆矩阵/hypnogram）来自 10 人重跑；② 人口学表按最终 10 人重新统计；③ 新被试知情同意/伦理手续可追溯，与 response letter 时间线一致。

### D3 反演模型 = 设备端已实现（表述修正）
`eeg_*.xls` 为口罩设备（Ref[48], IoTJ 2023）直接输出的 Fpz-Cz 导联波形。修改：II.B 明确信号由经 PSG 验证的设备输出；physics-informed 反演数学细节集中引至设备原理段（引 Ref[48] 公式与验证实验），满足 R1#2"讲清楚"。方法节不得暗示软件管线中另有一步转换。

### D4 源域协议 = Sleep-EDF 全集 + GroupKFold(subject)
- 数据：Sleep-EDF 2013 扩展子集全部记录（约 153 条、~80 被试；同一被试多夜记录必须**按 subject 分组**入同一折）；**Sleep-EDF 2012 子集（EDF-20）完全不参与训练，作跨数据集独立测试**。
- 切分：5-fold GroupKFold(subject)；纠正论文中"5-fold"与代码不符的历史表述。
- 预处理泄漏修复：scaler 仅在各折训练部分 fit。
- 滑窗：保留 10-epoch 上下文窗（subject 级切分下折内重叠合法，与 U-Time 等一致），论文写明输入形状。
- 平衡：**训练折内**平衡（随机欠/过采样，修复"取头部连续段"偏差，恢复 shuffle）；**测试折用自然分布**。
- 指标：Accuracy、**Cohen's κ**、macro-F1、per-class P/R/F1、混淆矩阵（真实计算直出）、均值±折间标准差。
- 特征：公式(2)为相对功率 → **改代码补算 ratio**（波段功率/总功率），与论文一致；全文频段符号统一（Δ、θ、α、β、γ 与 B_β 记法固定一种），回应 R1#4。

### D5 架构辩护 = 保留现架构 + 三件事
1. 论文写明模型输入为 **10 epochs × 10 features 序列**（澄清 R2#2 对"单向量"的误解），设计动机：轻量端侧部署（参数量/FLOPs 报出来）。
2. 补基线（同 subject-wise 协议）：① 单 epoch MLP；② 10-epoch 拼接 MLP；③ 目标域加 MLP/逻辑回归（30s epoch 统计特征）。证明 recurrent 结构与深度模型的增量价值。
3. Related Work 加 benchmark 表（本方案 vs DeepSleepNet/TinySleepNet + 现有 [45][46]，统一报 Acc/κ），讨论中**主动**将结果与 TinySleepNet κ=0.77–0.82、Fonseca κ=0.638/acc 77.8% 对标——把"98.64% 不合理"的批评转化为"我们的数字在文献坐标系内"。

### D6 目标域协议 = LOSO + 30s epoch + 诚实定位
- IMU 数据聚合到 **30s epoch**（对齐标签粒度；弃用 4.1M 行毫秒级随机切）。
- 10 人全部重跑标签迁移管线（新源域模型推理 → 伪标签 → 时间戳映射），修复推理端 scaler 重 fit 问题，报告 >0.95 置信过滤的保留率。
- 评估：**LOSO**（每人轮流做测试折），输出 per-subject 结果表 + 每人一张 hypnogram 图（回应 R2#6、AE）。
- **定位改写（防循环论证追打）:** 明确目标域指标度量的是"IMU 模型对 EEG 衍生伪标签的跨模态一致性"，非对照 PSG 精度；摘要/结论删去 "clinically viable"，降调为 proof-of-concept feasibility。
- 不补人工打分（已定）：伪标签 vs 专家标签 κ 验证列入 limitations + future work 明确承诺。

### D7 队列扩展 = 补 3 人全健康年轻（残余风险已接受）
无法满足"beyond 10"与人群多样性要求。缓解：response letter 承诺下一阶段临床队列（≥60 岁 + OSA AHI≥15）并已启动伦理申请；正文 limitations 相应强化。已知悉 R2#5 可能二审再提，接受此残余风险。

### D8 四分类问题 = 纯文字辩护
不补五分类实验。论据三点组合：① 已引 [34]（AASM inter-scorer：N1 一致性本最低）；② Fonseca 2023 同为 W/N1+N2/N3/REM 行业惯例先例；③ N1 类占比现实 + 伪标签链路拆 N1 属精度叠精度。写入 IV.D 讨论与 limitations。留活口：若二审坚持，5 折五分类半天可补。

### D9 新增引文 = 4 篇
1. A. Supratak & Y. Guo, "TinySleepNet: An efficient deep learning model for sleep stage scoring based on raw single-channel EEG," EMBC 2020, pp. 641–644, doi: 10.1109/EMBC44109.2020.9176741.
2. P. Fonseca et al., "A computationally efficient algorithm for wearable sleep staging in clinical populations," Sci. Rep., vol. 13, no. 9182, 2023, doi: 10.1038/s41598-023-36444-2.
3. A. Supratak, H. Dong, C. Wu, Y. Guo, "DeepSleepNet: A model for automatic sleep stage scoring based on raw single-channel EEG," IEEE Trans. Neural Syst. Rehabil. Eng., vol. 25, no. 11, pp. 1998–2008, 2017.
4. A. Supratak & P. Haddawy, "Quantifying the impact of data characteristics on the transferability of sleep stage scoring models," arXiv:2304.06033, 2023（终稿前查正式发表版本替换）.
用途：Related Work 段、benchmark 表、D6 结果对标、limitations 迁移性背书。U-Time/SleepNet/跨模态蒸馏系列暂不加，二审嫌薄随时补。

### D10 时间线与分工 = 8 周三线并行
| 周 | 轨道 A 新数据 | 轨道 B 实验 | 轨道 C 文稿 |
|---|---|---|---|
| W1-2 | 补采 3 人启动（叶尚乐/詹坚；伦理核对） | subject 列入 CSV；GroupKFold 改造；折内 scaler | D3 表述、符号统一、结论删图 |
| W3-4 | 完成 3 人 ×1-2 夜 | 源域 5-fold + MLP 基线 + EDF-20 独立测试 + κ | Related Work 改写（D9 引文入位） |
| W5-6 | — | 目标域 30s 聚合 + LOSO + hypnogram + per-subject 表 | 结果/讨论/摘要重写（真实数字） |
| W7-8 | — | 全表复核（脚本直出）+ 权重/日志归档 | Track Changes + response letter 定稿 |

服务器：`root@159.75.177.109`（PyCharm Python 3.7 pytorch 环境）。目标 **8 周内投出**（拖过 3-4 个月视同全新投稿换审稿人，不可控）。

---

## 二、审稿意见 → 修改动作映射表

| 意见 | 动作 | 决策号 |
|---|---|---|
| AE: subject-wise CV（源+目标） | GroupKFold(subject) + LOSO 全重跑 | D4/D6 |
| AE: RNN-LSTM 浅特征辩护 + MLP 基线 | 输入形状说明 + MLP 两型基线 | D5 |
| AE: Cohen's κ | 源域/目标域全部报 κ | D4/D6 |
| AE: hypnogram | 10 人每人一张 | D6 |
| AE: 目标域样本量+混淆矩阵 | per-subject 表 + 真实混淆矩阵直出 | D2/D6 |
| AE: 深化 SOTA | 4 新引文 + benchmark 表 + 跨模态迁移段（可选） | D5/D9 |
| AE: physics-informed 模型讲清楚 | 设备端输出 + 公式归位 Ref[48] | D3 |
| AE: 格式 | β/B 统一、结论区 Fig.4 移位删图、"5-fold"表述纠正、全文数字复核 | D1/D4 |
| AE: 扩展目标数据集 | +3 人（真实 N=10）+ 临床队列伦理承诺 | D2/D7 |
| R1#1 数据泄漏/过拟合 | D4 全案 + 新数字 + 折间标准差 + EDF-20 独立测试 | D4 |
| R1#2 反演模型表述 | D3 | D3 |
| R1#3 样本数/混淆矩阵缺失 | II.A 数据表（每人 epoch 数）+ IV 混淆矩阵（源+目标） | D4/D6 |
| R1#4 β→B、结论插图 | 符号统一；删图/移图 | AE 格式行 |
| R2#1 泄漏（详版） | 同 R1#1，response 中引用 U-Time/TinySleepNet κ 锚点自证合理区间 | D4/D5 |
| R2#2 浅特征深模型 | 输入形状 + MLP 基线 + 轻量部署论 | D5 |
| R2#3 目标域样本量 | 30s 聚合 + 真实 N + per-subject 表 + 一致性定位 | D6 |
| R2#4 N1 合并 | 三点文字辩护 | D8 |
| R2#5 健康年轻人群 | 部分回应（D7），limitations 强化 | D7 |
| R2#6 hypnogram | 每人一张 + NREM/REM 周期分析段 | D6 |
| R2 指定两篇 | 必引 | D9 |

## 三、预期结果与风险登记

- **源域预期:** subject-wise 后 Acc 大概率降至 ~83–88%、κ ~0.75–0.8（与 TinySleepNet 同数量级）——正常且可辩护。**摘要、结论、贡献(2)(3) 中所有 98.64%/89.77% 必须全部替换。**
- **目标域预期:** LOSO 跨被试一致性可能显著低于原 89.77%（单人训练→跨人是质变）。应对：如实报告 + 与 Fonseca（临床人群 κ=0.638）对标叙事 + 强调"标签迁移范式"本身仍是贡献主体。
- **风险 1:** R2#5 人群问题未完全关闭（D7 残余）。缓解=伦理承诺+措辞降调。
- **风险 2:** 补采 3 人的数据质量/完整度不可控。缓解=多备 1-2 名候选志愿者；若最终 N<10，论文如实写真实 N（不得回退到虚报）。
- **风险 3:** 目标域 89.77% 无出处且不可复现——重跑后无论涨跌都以新数字为准，response letter 中不解释旧数字，只呈现新协议新结果。

## 四、后续动作

1. 本文档经 `/plan-review` 审查后，拆解为实施计划（`docs/superpowers/plans/`）：管线改造代码任务、实验任务、文稿改写任务。
2. response letter 初稿在 W5 实验数字出炉后起草（逐条引用本文档映射表）。
3. 全部训练在远程服务器执行并留存日志/权重；本地 `sleep_classify` 仓库改动前 `git status`（分支 release.new）。
