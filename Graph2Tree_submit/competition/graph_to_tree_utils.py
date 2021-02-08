# coding: utf-8

# Graph2Tree_submit/competition/data_process_group_num.py
# 中的配置：
# 用于切换处理比赛的训练、测试集
# TARGET_FILE_GROUP_NUM = 'train_corrected'
TARGET_FILE_GROUP_NUM = 'test'

# Graph2Tree_submit/competition/graph2tree.py
# 中的配置：
# 人工干预模型是否训练结束，True则确定开始预测，False则继续训练（如果训练轮数已经完成，则开始预测）
TRAIN_ITERATION_OVER = True

# 每个问题至多使用的增强数据数量，<=0 表示不使用增强的数据，仅使用原始数据
USE_EDA = -1

# 模型训练超参数
batch_size = 64
embedding_size = 128
hidden_size = 512
n_epochs = 80
learning_rate = 1e-3
weight_decay = 1e-5
beam_size = 5
n_layers = 2
