# Manuscript_V1 可直接执行的文字修改（前后对照）

**配套文档:** `2026-09-04-iotj-revision-plan.md`（决策 D1-D10）
**原则:** 以下修改不依赖新实验结果，可立即在 Word 中以 Track Changes 执行。所有 `【…】` 为实验重跑后填入的占位符（占位符本身先写入，数字后补）。原文以 Manuscript_V1.docx 实际文本为准。

---

## E1. Abstract — 替换虚高数字 + 定位改写

**原文**
> Experi-mental results indicate that an accuracy of 98.64% and an F1-score of 98.63% are achieved by the RNN-LSTM model in the EEG source domain. In the IMU target domain, an accuracy of 89.77% and an F1-score of 89.76% are attained by the CNN-RNN hybrid model.

**改为**
> Experimental results, obtained under strict subject-wise evaluation, indicate that the RNN-LSTM model achieves an accuracy of 【XX.X ± X.X】% (macro F1 【XX.X】%, Cohen's κ 【0.XX】) in the EEG source domain under five-fold subject-level cross-validation, and 【XX.X】% on an independent cross-dataset test (Sleep-EDF 2012 subset). In the IMU target domain, the CNN-RNN hybrid model attains an accuracy of 【XX.X】% (κ 【0.XX】) under a leave-one-subject-out protocol, quantifying the cross-modal consistency with which EEG-derived transferred labels are reproduced from inertial signals alone.

**依据:** D4/D6；R1#1、R2#1/#3。

---

## E2. Introduction — 反演模型表述（含义 A：设备端）

**原文（引言第 4 段）**
> The raw neurophysiological signals from the portable EEG system are converted into Fpz–Cz-like EEG waveforms via a physics-informed mathematical inversion model.

**改为**
> The portable EEG system outputs single-channel waveforms in the Fpz–Cz montage; the underlying physics-informed inversion, which recovers cortical activity from the device-coupled bio-potential signals, was formulated and validated against PSG in our prior work [48]. Section II.B describes its interface to the proposed pipeline; no additional conversion is applied in this study.

**依据:** D3；R1#2、AE"clarify the physics-informed mathematical model"。

---

## E3. Introduction — 贡献 (2) 重写

**原文**
> (2) The RNN-LSTM is validated as a high-precision source-domain label generator on the Sleep-EDF dataset [47]. An accuracy of 98.64% is achieved in the four-class sleep staging task using only Fpz–Cz EEG, providing robust and reliable supervisory signals for subsequent label transfer.

**改为**
> (2) The RNN-LSTM is validated as a source-domain label generator on the extended Sleep-EDF dataset under a strict subject-wise protocol (five-fold cross-validation with all recordings of a given subject confined to the same fold, plus an independent test on the 2012 subset). An accuracy of 【XX.X】% with Cohen's κ of 【0.XX】 is achieved in the four-class sleep staging task using only Fpz–Cz EEG, placing the source-domain performance within the range reported by state-of-the-art single-channel EEG stagers on the same benchmark 【refs D9-1/3】 and thereby providing supervision of verified quality for subsequent label transfer.

**依据:** D4/D5/D9；R1#1（把"超高"改叙事为"与 SOTA 同区间且协议严格"）。

---

## E4. Introduction — 贡献 (3) 重写

**原文**
> (3) High-accuracy sleep staging is achieved using only inertial signals: with only triaxial acceleration and angular velocity inputs, the lightweight CNN-RNN model attains a four-class accuracy of 89.77%, significantly outperforming conventional rule-based methods (~78%).

**改为**
> (3) Feasible sleep staging is demonstrated using only inertial signals: the lightweight CNN-RNN model (【X】k parameters, 10 Hz-frame inputs) reproduces EEG-transferred four-class labels with a leave-one-subject-out accuracy of 【XX.X】% (κ 【0.XX】), exceeding the ~78% of conventional rule-based methods. Because the reference standard in this domain consists of model-generated pseudo-labels, the reported figures quantify cross-modal consistency rather than agreement with expert PSG scoring, and are interpreted as proof-of-concept evidence for label-transfer-enabled home monitoring.

**依据:** D6 防循环论证；R2#3/#5；AE 临床声明降调。

---

## E5. Section II.A — 频段定义与符号统一（回应 R1#4"beta→B"）

**原文（公式 (2) 附近）**
> Frequency-domain features: relative power () calculated for the five frequency bands (Delta, Theta, Alpha, Beta, and Gamma). is defined as the ratio of the integrated power of a specific band to the total power across all bands...

**改为**
> Frequency-domain features: the *relative band power* R_b, b ∈ {δ, θ, α, β, γ}, computed over five bands following AASM conventions — δ (0.5–4 Hz), θ (4–8 Hz), α (8–13 Hz), β (13–30 Hz), γ (30–40 Hz). For band b, R_b is defined as
> R_b = ( ∫_{f∈b} P(f) df ) / ( ∫_{0.5}^{40} P(f) df )   (2)
> where P(f) denotes the power spectral density estimated by Welch's method. The symbol R_b is used consistently throughout this paper; Σ_b R_b = 1.

⚠️ 连带项：① Fig.1 波形示意图中 "Alpha 8–12 Hz"、"Gamma 30–80 Hz" 需同步改（PPT 源文件里就是错的）；② 代码特征提取 `alpha 8-12 / beta 12-30` 边界改为 `8-13 / 13-30`（D4）。

**依据:** R1#4、D4。

---

## E6. Section II.A — 被试数与切分协议表述

**原文**
> To balance data diversity and computational efficiency, data from 80 participants were randomly selected from this dataset for model development.

**改为**
> The complete 2013 extended cohort (SC subset; 【153】 overnight recordings from 【80】 subjects) was used for model development. To prevent within-subject information leaking across splits, all recordings of the same subject were assigned to the same fold, and evaluation followed a five-fold cross-validation grouped by subject (GroupKFold). In addition, the independent 2012 subset (【20】 recordings) was retained exclusively for cross-dataset testing.

**依据:** D4；R1#1、R2#1。

---

## E7. Section II.A — 输入形状与架构辩护（回应 R2#2"浅特征深模型"）

**在 II.A 模型描述处（或 III.A 引用 Fig.3 处）插入**
> Each sample is a sequence of 10 consecutive 30-s epochs, each represented by a 10-dimensional feature vector; the RNN-LSTM thus operates on a 10 × 10 input tensor and models cross-epoch transitions, which a per-epoch classifier cannot represent. Two multilayer-perceptron baselines — one operating on a single epoch and one on the flattened 10-epoch window — were evaluated under the identical subject-wise protocol (Table 【X】). This handcrafted-feature design keeps the entire source-domain model below 【X】k parameters, consistent with the lightweight edge-deployment orientation of the proposed system.

**依据:** D5；R2#2（正面回应"nor compare it to a simple MLP baseline"）。

---

## E8. Section II.A — 类别平衡表述（纠正旧偏方案）

**原文**
> Subject sequences with relatively balanced distributions across the four classes were prioritized; furthermore, for individuals with severe imbalance, an undersampling strategy was employed to remove redundant N2 samples.

**改为**
> Within each training fold only, the four classes were balanced by stratified random undersampling of the majority class. Test folds retain the natural epoch distribution of each subject, so that the reported accuracy, per-class F1, and Cohen's κ reflect real-world prevalence rather than an artificially balanced population.

**依据:** D4（修复"取头部连续段"偏差；R1#1 overfitting 关切）。

---

## E9. Section II.B — 反演模型在方法节的落点（与 E2 配套）

**原文**
> The portable EEG system [48] was employed to capture weak scalp physiological pulse signals synchronized with cortical electrical activity. These signals are converted into frontal single-channel EEG-like time-series waveforms via a validated physics-informed mathematical inversion model.

**改为**
> The portable EEG system [48] acquires the weak scalp bio-potential coupled with cortical activity. Its embedded physics-informed inversion algorithm — formulated in [48], where it was validated against simultaneously recorded PSG (agreement κ = 【0.XX，从 Ref48 原文核对后填】) — outputs a single-channel EEG waveform in the Fpz–Cz montage in real time at 100 Hz. The acquisition chain therefore delivers ready-to-score Fpz–Cz-like signals; no additional inversion is performed downstream in the proposed pipeline.

**依据:** D3；R1#2。

---

## E10. Section II.B — 被试段（真实 N + 样本量表 + 措辞）

**原文**
> A total of 10 healthy adult volunteers (7 males, 3 females; aged 22–35 years, mean age 26.4 ± 3.8 years) were recruited.

**改为**
> A total of 10 healthy adult volunteers (【X males, X females; aged 22–35 years, mean age XX.X ± X.X years】) were recruited between 【2025-07】 and 【2026-XX】; the cohort composition will be reported exactly as recorded in the updated Table II, which additionally lists, per participant, the number of valid nights, the number of 30-s epochs collected, and the number retained after confidence filtering.

**原文**
> This study serves as an initial feasibility validation; a sample size of 10 participants is considered sufficient to demonstrate the technical feasibility of the label transfer approach.

**改为**
> This study is designed as a proof-of-concept feasibility validation with a correspondingly small cohort; results should be interpreted as evidence of methodological feasibility rather than of clinical accuracy, and power for subgroup analysis is limited.

**依据:** D2/D6/D7；R2#3/#5、AE sample sizes。

---

## E11. Section II.C — 伪标签定位 + LOSO 协议

**原文**
> For each 30-second epoch, sleep stage labels with prediction probabilities exceeding 0.95 were retained as high-confidence pseudo-labels, by which manual expert annotation was effectively replaced.

**改为**
> For each 30-second EEG epoch, predictions with softmax probability exceeding 0.95 were retained as high-confidence pseudo-labels (overall retention rate 【XX.X】%; per-subject rates in Table II). These transferred labels constitute the reference standard of the target domain. We emphasize that target-domain models are trained to reproduce EEG-derived pseudo-labels from inertial signals; all reported target-domain metrics therefore quantify cross-modal consistency, not agreement with human-expert PSG scoring. Expert AASM rescoring of the recorded EEG nights to quantify pseudo-label reliability (κ against human scorers) is planned as the next stage of validation.

**原文**
> To evaluate the models, an 80/20 train-test split was applied to ensure robust performance evaluation.

**改为**
> All IMU epochs were aggregated to the 30-s label granularity before modeling. To assess genuine cross-subject generalization, evaluation followed a leave-one-subject-out protocol: for each of the 10 participants, the model was trained on all epochs of the remaining nine participants and tested on the held-out participant, ensuring that no epoch, nor any temporal neighbor of any epoch, of a given subject appears in both training and test data. Feature standardization (Eq. 4) was fitted on the training partition of each fold only.

**依据:** D6；R2#1/#3、AE subject-wise 要求、防"epoch 泄漏"追打。

---

## E12. Section III.A — 源域结果句（占位）

**原文**
> ...attains an accuracy of 98.64% and an F1-score of 98.63%.

**改为**
> ...attains an accuracy of 【XX.X ± X.X】% and a macro F1-score of 【XX.X ± X.X】% (Cohen's κ 【0.XX ± 0.0X】), where values are means ± standard deviations across the five subject-level folds.

**同段** "prediction accuracies of 99.6% and 96.7%..." → 占位重写，且 Fig.2(b) 必须换成重跑脚本直出的混淆矩阵（旧图为手填，D4/诚信红线）。

---

## E13. Section IV.A — 评价指标定义补 κ

**在公式 (5) 后插入**
> In addition, Cohen's κ coefficient was reported for both domains as the chance-corrected measure of epoch-level agreement, together with per-class precision, recall, and F1, and unnormalized confusion matrices stating absolute epoch counts (Tables 【I–II】 and Fig. 【2b/4b】). κ is reported because accuracy alone is known to overstate agreement in sleep staging when class distributions are skewed 【ref: Fonseca 2023】.

**依据:** AE"report Cohen's kappa"；R1#3"exact sample sizes"。

---

## E14. Section IV.A — hypnogram 段落新增（对应新图）

**新增一段（放 IV.B 末尾）**
> Fig. 【5】 shows representative hypnograms of 【three】 participants comparing the transferred labels with CNN-RNN predictions under the leave-one-subject-out protocol. The predicted sequences reproduce the expected macroarchitectural progression — consolidated deep sleep in the first cycles and lengthening REM episodes in the second half of the night — indicating that the model captures hypnogram-level structure rather than isolated epochs; residual errors concentrate at stage transitions, consistent with their inherent scoring ambiguity 【ref: Rosenberg & Van Hout 2013, 即现稿 [34]】.

**依据:** R2#6、AE hypnogram。

---

## E15. Related Work/Introduction 第 3 段 — 深化 SOTA（D9 四篇入位）

**新增句子（插入 Introduction 第 3 段末或独立段）**
> In single-channel EEG staging, lightweight architectures such as DeepSleepNet 【ref D9-3】 and TinySleepNet 【ref D9-1】 report accuracies of ~83–85% with Cohen's κ of 0.77–0.82 on Sleep-EDF — figures close to inter-rater agreement among human scorers, which bounds what any automated stager should be expected to achieve on this dataset. Consequently, results materially above this range warrant scrutiny of the evaluation protocol, particularly whether training and test data share subjects or overlapping windows. For non-EEG alternatives, a computationally efficient wearable 4-class algorithm (Wake, N1+N2, N3, REM) validated in clinical populations attained 77.8% accuracy with median κ = 0.638 【ref D9-2】, establishing a realistic reference point for staging from motion- and cardiac-related surrogates. At the modality-transfer level, quantitative studies show that EEG staging models degrade appreciably across subjects and datasets unless aligned 【ref D9-4】, motivating the hardware-synchronized, subject-separated validation design adopted in this work.

**依据:** AE"deepen the analysis of the state of the art"；审稿人指定 2 篇；D5 叙事锚点。

---

## E16. Conclusion — 数字、降调、删图、limitations

1. **结构（R1#4）:** 把 Fig. 4（CNN-RNN 架构图）从 Conclusion 正文中移出，改置于 Section II.C/III.B 首次引用处；Conclusion 区不得残留任何图。
2. **原文** "This performance approaches the lower bound of clinical acceptability for automated sleep scoring, despite relying solely on unobtrusive, contactless sensing."
   **改为** "Taken together, these results provide proof-of-concept evidence that synchronized EEG-guided label transfer can bootstrap contactless sleep staging beyond rule-based baselines; establishing clinical-grade accuracy will require expert-scored validation and diverse clinical cohorts in future work."
3. **limitations 段** "such as Temporal Convolutional Networks (TCNs), Transformer-based architectures..." 之后加：
   > Third, the target-domain reference standard consists of model-generated pseudo-labels; agreement between these labels and expert AASM scoring has not yet been measured and will be quantified via expert rescoring of the recorded EEG. Fourth, although the transferred labels exhibit physiologically plausible macroarchitecture, cross-modal consistency metrics upper-bound at the reliability of their reference and should not be read as PSG-validated accuracy.
4. **future work 首条** 补"…for which ethics application has been initiated."（D7 承诺落地）。
5. 摘要/结论中所有"clinical viability / practically scalable solution for accurate home-based sleep monitoring"类措辞统一降调为 feasibility/proof-of-concept。

**依据:** D6/D7；R2#5；AE。

---

## E17. 格式清扫清单（随手改，无需决策）

| 位置 | 问题 | 处理 |
|---|---|---|
| Abstract/II.A/III.A | 断词残留 "Experi-mental"、"overrepres-entation"、"charac-teristics" | 恢复原词 |
| IV.A | "Deep Sleep (Deep Sleep/N3)" 重复 | 改 "Deep Sleep (N3)" |
| 全文 | 频段符号（E5 的 R_b 约定）与下标正斜体统一 | 按 E5 |
| Fig.1 | 图中 Alpha 8–12 / Gamma 30–80 与正文不符 | 重画 |
| Fig.2 | 横轴 "Stage 1/Stage 2" 未映射类别 | 改 Wake/Light/Deep/REM |
| Refs | [42] IEEE OJEMBS 卷号页码格式、[25] 缺页码城市项 | 补全 |
| 全文 | 任何与新数字冲突的旧数字（搜 "98.6"、"89.7"、"0.95"、"5-fold"） | 占位符替换后终检 |

---

## 依赖提醒

- E1/E3/E4/E10/E12/E16 含占位符，**W5 数字出来前不得定稿**，但可以先以 Track Changes 写入结构句。
- 执行顺序建议：E2/E5/E6/E8/E9/E11/E13/E14/E15/E17（纯表述，立即完成）→ 数字类待实验。
- Word 中全部修改必须开 Track Changes（编辑部硬性要求）。
