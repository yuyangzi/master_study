## 睡姿分类子项目（sleep_classify）

这是一个基于IMU数据的睡姿分类子项目（左卧/仰卧/右卧）。

### 结构
- code/：9个独立训练脚本
- after_process_data/after_process_data/：165个.xlsx数据文件
- model/：模型存储目录（初始为空）
- util/：辅助工具

### Git状态
独立Git仓库，当前分支：release.new。工作区不干净：code/*.py已修改，README.md和myplot.png已被删除。

### 入口点
所有9个脚本均为独立入口。bp_algorithm.py通过t0()调用，其余使用if __name__ == "__main__"。

### 数据命名
{name}{num}{posture}.xlsx，posture=left/m/right。*_motion.xlsx不参与训练。

### 运行规范
必须cd到code/目录下执行。使用相对路径：../after_process_data/...。禁止从工作区根目录运行。

### 模型存储
verify_model.py期望加载 ../model/kd_tree.m（当前为空目录）。

### 特征与分类
6个IMU特征：feature1–feature6。3类分类任务：左卧(0)、仰卧(1)、右卧(2)。

### 反模式
禁止未经用户许可执行git add/commit/push。禁止恢复已删除的README.md文件。