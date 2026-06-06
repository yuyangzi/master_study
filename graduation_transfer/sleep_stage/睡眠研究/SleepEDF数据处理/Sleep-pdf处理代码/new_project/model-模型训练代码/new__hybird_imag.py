import matplotlib
# 如果 PyCharm 报错，请取消下面这行的注释
# matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 1. 准备数据 (基于您提供的数据特征)
data = [
    [99.6,  0.4,  0.0,  0.0],  # Wake
    [ 0.0, 97.6,  0.2,  2.2],  # Stage 1
    [ 0.0,  0.4, 99.6,  0.0],  # Stage 2 (深睡期 99.8%)
    [ 0.0,  3.3,  0.0, 96.7]   # REM (快速眼动 96.7%)
]

labels = ['Wake', 'Stage 1', 'Stage 2', 'REM']
df_cm = pd.DataFrame(data, index=labels, columns=labels)

# 2. 设置画布
plt.figure(figsize=(10, 8))

# 3. 绘制热力图
# annot_kws={"size": 16, "weight": "bold"} 直接统一加大加粗数字
ax = sns.heatmap(df_cm, annot=True, fmt=".1f", cmap="YlGnBu",
                 linewidths=1.5, linecolor='white',
                 annot_kws={"size": 16, "weight": "bold"},
                 cbar_kws={'label': 'Accuracy (%)'})

# 4. 细节微调：确保不同背景下的文字清晰度
for t in ax.texts:
    val = float(t.get_text().replace('%', ''))
    t.set_text(f"{val}%")
    # 对角线或高数值使用白色，其余使用黑色
    if val > 40:
        t.set_color('white')
    else:
        t.set_color('black')

# 5. 加大坐标轴标签和标题
# plt.title('Sleep Stage Classification Confusion Matrix', pad=25, fontsize=18, fontweight='bold')
plt.xlabel('Predicted Label', fontsize=14, fontweight='bold')
plt.ylabel('True Label', fontsize=14, fontweight='bold')
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.tight_layout()

# 6. 保存与显示
plt.savefig('confusion_matrix_bold.png', dpi=300)
plt.show()