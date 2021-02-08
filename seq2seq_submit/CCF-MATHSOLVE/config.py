# 基本参数
maxlen = 160
# NVIDIA Tesla V100 16G: bert_base 32, roberta 30, roberta_large 10
batch_size = 32
epochs = 35

# bert配置
config_path = './pretrain/bert/bert_config.json'
checkpoint_path = './pretrain/bert/bert_model.ckpt'
dict_path = './pretrain/bert/vocab.txt'

# 使用eda的数量， 如每个问题至多使用3个eda，这样总量就会×4（理论上）
use_eda = 4

# 是否过滤运算符数量大于4的表达式
operator_no_gt_4 = True

# 训练数据路径
data_path = './data/train_corrected_processed_eda.json'

# 生成模型权重的路径
model_path = './model/best_model_eda7_gt4_bert.weights'

# 是否不经过训练，直接加载训练好的模型；
# ''为否，
# 非空则为是，填入具体路径为待加载模型地址，如：'./model/best_model_eda7_gt4_bert.weights'
model_load_path = ''

# 生成训练损失log的路径
loss_log_path = './log/log_eda7_bert.txt'

# 测试数据的路径
test_path = './data/test.csv'

# 预测文件的路径
pred_path = './data/train_eda7_op4_bert.csv'
