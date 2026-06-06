"""
用于生成各模型性能指标的条形图，用于SCI论文
显示准确率、精确率、召回率和F1-score
"""
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免显示窗口错误
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

# 设置字体和样式（用于SCI论文）
plt.rcParams['font.family'] = 'Arial'  # 使用Arial字体（SCI论文常用）
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0
plt.rcParams['xtick.minor.width'] = 0.5
plt.rcParams['ytick.minor.width'] = 0.5
sns.set_style("white")

# 数据准备
# 显示名称（用于图表标签）
models = ['KNN', 'Decision Tree', 'CNN', 'RNN', 'LSTM', 'RNN-LSTM']
# 数据键名（用于数据字典）
model_keys = ['KNN', 'DecisionTree', 'CNN', 'RNN', 'LSTM', 'RNN-LSTM']

# 数据：准确率、精确率、召回率、F1-score（按顺序）
data = {
    'KNN': [82.73, 82.69, 82.91, 82.70],
    'DecisionTree': [76.84, 76.99, 77.04, 76.63],
    'CNN': [86.74, 87.13, 86.74, 86.69],
    'RNN': [88.50, 88.46, 88.64, 88.52],
    'LSTM': [84.19, 84.10, 84.35, 84.20],
    'RNN-LSTM': [98.64, 98.66, 98.62, 98.63]
}

# 指标名称
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-score']

# 创建图形（调整尺寸比例，更适合论文）
fig, ax = plt.subplots(figsize=(10, 5.5))

# 设置条形图的宽度和位置
x = np.arange(len(models))  # 模型位置
width = 0.19  # 每个条形的宽度
spacing = 0.01  # 条形之间的间距

# 定义颜色（适合SCI论文的专业配色 - 使用柔和的颜色，避免过于鲜艳）
# 使用不同深浅的蓝色系和灰色系，更专业
colors = ['#4472C4', '#ED7D31', '#70AD47', '#FFC000']  # 蓝色、橙色、绿色、黄色（专业配色）

# 绘制每个指标的条形图
for i, (metric, color) in enumerate(zip(metrics, colors)):
    values = [data[model_key][i] for model_key in model_keys]
    offset = (i - 1.5) * (width + spacing)  # 计算偏移量，使条形居中
    bars = ax.bar(x + offset, values, width, label=metric, color=color, 
                   edgecolor='white', linewidth=0.8, alpha=0.85)
    
    # 在每个条形上添加数值标签（竖着展现，保留2位小数，带百分号，加粗）
    for bar in bars:
        height = bar.get_height()
        # 标签放在条形顶部上方，竖着展现
        ax.text(bar.get_x() + bar.get_width()/2., height + 1.0,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=8, fontweight='bold',
                rotation=90)  # 旋转90度，竖着展现

# 设置x轴标签和位置（SCI论文中常用无轴标题，仅保留刻度标签）
# ax.set_xlabel('Models', fontsize=12, fontweight='normal', labelpad=8)
ax.set_ylabel('Performance (%)', fontsize=12, fontweight='normal', labelpad=8)
# 移除标题（SCI论文通常不需要图表标题，标题在caption中）
# ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=11, fontweight='bold')
ax.set_ylim([70, 103])  # 设置y轴范围，留出空间显示竖着的标签

# 设置y轴刻度
ax.set_yticks(np.arange(70, 101, 5))
ax.tick_params(axis='both', which='major', labelsize=10)

# 添加图例（简洁风格，无阴影）
ax.legend(loc='upper left', frameon=True, fancybox=False, shadow=False, 
          fontsize=10, framealpha=0.9, edgecolor='gray', facecolor='white')

# 添加网格线（y轴方向，更精细）
ax.grid(axis='y', linestyle='-', alpha=0.2, linewidth=0.5, zorder=0)
ax.set_axisbelow(True)  # 将网格线放在条形图后面

# 设置边框样式
for spine in ax.spines.values():
    spine.set_linewidth(1.0)
    spine.set_color('black')

# 调整布局（增加边距，更适合论文）
plt.tight_layout(pad=2.0)

# 创建输出目录
output_dir = "./figures"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 保存为高分辨率图片（适合SCI论文）
plt.savefig(os.path.join(output_dir, 'model_performance_bar_chart.png'), 
            dpi=300, bbox_inches='tight', facecolor='white')
print(f"条形图已保存到: {os.path.join(output_dir, 'model_performance_bar_chart.png')}")

# 保存为PDF（矢量图，适合论文）
plt.savefig(os.path.join(output_dir, 'model_performance_bar_chart.pdf'), 
            bbox_inches='tight', facecolor='white')
print(f"条形图已保存到: {os.path.join(output_dir, 'model_performance_bar_chart.pdf')}")

# 关闭图形以释放内存（使用非交互式后端时不需要显示）
plt.close()

print("\n各模型性能指标:")
print("-" * 80)
print(f"{'Model':<15} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-score':<12}")
print("-" * 80)
for model, model_key in zip(models, model_keys):
    acc, prec, rec, f1 = data[model_key]
    print(f"{model:<15} {acc:<12.2f}% {prec:<12.2f}% {rec:<12.2f}% {f1:<12.2f}%")

