
# 解答数学题

## 环境

keras2.2.4+numpy1.16.1+tensorflow-gpu1.13+python3.5
(具体参考Requirements.txt)

进入该[网站](https://github.com/ymcui/Chinese-BERT-wwm#%E4%B8%AD%E6%96%87%E6%A8%A1%E5%9E%8B%E4%B8%8B%E8%BD%BD)下载预训练模型[bert](https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip)、[RoBERTa](https://drive.google.com/open?id=1jMAKIJmPn7kADgD3yQZhpsqM-IRM1qZt)和[Robert_large](https://drive.google.com/open?id=1dtad0FFzG11CBsawu8hvwwzU2R0FDI94)至pretrain文件夹下

## 运行步骤

``shell
cd CCF-MATHSOLVE/
python train.py
``

通过运行train.py，可以得到含有权重的模型和预测的文本结果。

**NOTE**

文件config.py中含有可调参数为：
    
    参数use_eda：表示使用eda数量,
    参数operator_no_gt_4：bool值，表示是否过滤运算符数量大于4个的表达式，
    参数batch_size,
    参数epochs

(注：本次使用的模型共8个，分别为eda3_op4_bs25_RoBERTa,eda3_op4_bs30_BERT, eda3_op4_bs30_RoBERTa, eda4_op4_bs30_RoBERTa, eda5_gt4_bs30_RoBERTa, train_eda6_op4_bs30_RoBERTa, train_eda7_op4_bs30_RoBERTa, eda4_op4_bs30_RoBERTalarge.其中eda3表示参数use_eda=3, op4表示operator_no_gt_4=True, bs30表示batch_size=30, BERT表示使用的预训练模型为bert_base)
