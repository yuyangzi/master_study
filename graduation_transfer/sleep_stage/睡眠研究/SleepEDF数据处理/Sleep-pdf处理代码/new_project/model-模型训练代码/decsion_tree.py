"""
使用knn的算法进行PSG的睡眠阶段的预测
"""
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
import pandas as pd


class DecisionTreeAlgorithm(object):

    def __init__(self):
        # 数据集所在的文件夹
        self.dir_path = "F:/master_paper_and_project/research/new_project/merge_data/balanced_sort_2025_09_15_21_data.csv"

    def kdree_train_data(self):
        """
        用于处理对应的相关数据
        :return:
        """
        df = pd.read_csv(self.dir_path)
        value_to_remove = ['Movement time', 'Sleep stage ?']
        df = df[~df['label'].isin(value_to_remove)]
        le = LabelEncoder()
        df['label'] = le.fit_transform(df['label'])
        scaler = StandardScaler()
        # 获取对应的数据集
        X = scaler.fit_transform(df.drop('label', axis=1))
        y = df['label']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 定义 KNN 分类器
        algo = DecisionTreeClassifier(max_depth=7, min_samples_split=3, criterion="gini")

        # 训练模型
        algo.fit(X_train, y_train)

        # 测试模型
        y_pred = algo.predict(X_test)

        # 准确率

        accuracy = accuracy_score(y_test, y_pred)

        # 精准率、召回率和 F1-Score（基于宏平均）
        precision = precision_score(y_test, y_pred, average='macro')
        recall = recall_score(y_test, y_pred, average='macro')
        f1 = f1_score(y_test, y_pred, average='macro')

        # 输出结果
        print("Decision tree Model Performance:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")

        # 分类报告（包括每个类的指标）
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    DecisionTreeAlgorithm().kdree_train_data()





