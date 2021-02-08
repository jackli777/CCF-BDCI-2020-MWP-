import copy
import csv
import os
import pprint

# 用以比较B榜提交的评测和我们对于来自seq2seq重新生成，后又进行融合的结果
# file_raw = '../submits/submit_voted_merged_B_4.B榜提交评测.csv'
# file_mod = '../submits/submit_voted_merged_B_4.B榜其中单模来自seq2seq重新生成的模型的结果.csv'

# 用以比较B榜提交的评测和我们对于来自seq2seq重新生成，后又进行融合的结果2
# file_raw = '../submits/submit_voted_merged_B_4.B榜提交评测.csv'
# file_mod = '../submits/submit_voted_merged_B_4.B榜其中单模来自seq2seq重新生成的模型的结果2.csv'

# 用以比较B榜提交的评测和我们对于来自seq2seq重新生成，两次重新生成的结果
# file_raw = '../submits/submit_voted_merged_B_4.B榜其中单模来自seq2seq重新生成的模型的结果.csv'
# file_mod = '../submits/submit_voted_merged_B_4.B榜其中单模来自seq2seq重新生成的模型的结果2.csv'

# 用以比较“07-生成单模答案-02”中所述的，用来实验验证seq2seq方案在模型训练过程中的随机性：
file_raw = '../from_seq2seq/B_stochastic_test/train_eda4_op4_robert_newpost.csv'
file_mod = '../from_seq2seq/B_stochastic_test/train_eda4_op4_Robert_newpost_new.csv'

ans_dict_raw = {}
with open(file_raw, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        ans_dict_raw[row[0]] = row[1]

ans_dict_mod = {}
with open(file_mod, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        ans_dict_mod[row[0]] = row[1]

counter_discrepency = 0
print('doc_index, ans_raw, ans_mod:')
for doc_index in ans_dict_raw:
    if ans_dict_raw[doc_index] != ans_dict_mod[doc_index]:
        counter_discrepency += 1
        print(doc_index, ans_dict_raw[doc_index], ans_dict_mod[doc_index])
print()

print('counter_discrepency: ', counter_discrepency,
      'percentage: ', counter_discrepency/len(ans_dict_raw))
print()
