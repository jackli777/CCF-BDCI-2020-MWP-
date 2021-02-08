#! -*- coding: utf-8 -*-

from __future__ import division

import json
import random
import re

import numpy as np
import pandas as pd
from bert4keras.backend import K, keras
from bert4keras.layers import Loss
from bert4keras.models import build_transformer_model
from bert4keras.optimizers import Adam
from bert4keras.snippets import (AutoRegressiveDecoder, DataGenerator, open,
                                 sequence_padding)
from bert4keras.tokenizers import Tokenizer, load_vocab
from keras.callbacks import ModelCheckpoint
from keras.models import Model
from sympy import Integer
from tqdm import tqdm

from config import (batch_size, checkpoint_path, config_path, data_path,
                    dict_path, epochs, loss_log_path, maxlen, model_load_path,
                    model_path, pred_path, test_path)
from load_eda_data import load_train_data
from utils import (char_unify_convertor, convert_cn_colon_to_en,
                   convert_en_punct_to_cn, convert_some_mentions, del_spaces,
                   generate_ans_and_post_process_for_competition_format,
                   replace_1_with_l, replace_l_with_1, rm_pinyin_yinjie,
                   units_mention_unify)

# 加载数据
data_d = load_train_data(data_path)
random.seed(42)
random.shuffle(data_d)
train_data = data_d
# 加载并精简词表，建立分词器
token_dict, keep_tokens = load_vocab(
    dict_path=dict_path,
    simplified=True,
    startswith=['[PAD]', '[UNK]', '[CLS]', '[SEP]'],
)
tokenizer = Tokenizer(token_dict, do_lower_case=True)


class data_generator(DataGenerator):
    """数据生成器
    """

    def __iter__(self, random=False):
        batch_token_ids, batch_segment_ids = [], []
        for is_end, (question, equation, answer) in self.sample(random):
            token_ids, segment_ids = tokenizer.encode(
                question, equation, maxlen=maxlen
            )
            batch_token_ids.append(token_ids)
            batch_segment_ids.append(segment_ids)
            if len(batch_token_ids) == self.batch_size or is_end:
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                yield [batch_token_ids, batch_segment_ids], None
                batch_token_ids, batch_segment_ids = [], []


class CrossEntropy(Loss):
    """交叉熵作为loss，并mask掉输入部分
    """

    def compute_loss(self, inputs, mask=None):
        y_true, y_mask, y_pred = inputs
        y_true = y_true[:, 1:]  # 目标token_ids
        y_mask = y_mask[:, 1:]  # segment_ids，刚好指示了要预测的部分
        y_pred = y_pred[:, :-1]  # 预测序列，错开一位
        loss = K.sparse_categorical_crossentropy(y_true, y_pred)
        loss = K.sum(loss * y_mask) / K.sum(y_mask)
        return loss


model = build_transformer_model(
    config_path,
    checkpoint_path,
    application='unilm',
    keep_tokens=keep_tokens,  # 只保留keep_tokens中的字，精简原字表
)

output = CrossEntropy(2)(model.inputs + model.outputs)

model = Model(model.inputs, output)
model.compile(optimizer=Adam(2e-5))
model.summary()


class AutoSolve(AutoRegressiveDecoder):
    """seq2seq解码器
    """
    @AutoRegressiveDecoder.wraps(default_rtype='probas')
    def predict(self, inputs, output_ids, states):
        token_ids, segment_ids = inputs
        token_ids = np.concatenate([token_ids, output_ids], 1)
        segment_ids = np.concatenate(
            [segment_ids, np.ones_like(output_ids)], 1)
        return model.predict([token_ids, segment_ids])[:, -1]

    def generate(self, text, topk=3):
        token_ids, segment_ids = tokenizer.encode(text, maxlen=maxlen)
        output_ids = self.beam_search([token_ids, segment_ids],
                                      topk)  # 基于beam search
        return tokenizer.decode(output_ids).replace(' ', '')


autosolve = AutoSolve(start_id=None, end_id=tokenizer._token_end_id, maxlen=32)


class Evaluator(keras.callbacks.Callback):
    """保存loss
    """

    def on_train_begin(self, logs={}):
        self.losses = []

    def on_epoch_end(self, epoch, logs={}):
        model.save_weights(model_path)  # 保存模型
        self.losses.append(logs.get('loss'))


def predict(in_file, out_file, topk=3):
    """输出预测结果到文件
    """
    fw = open(out_file, 'w', encoding='utf-8')
    raw_data = pd.read_csv(in_file, header=None, encoding='utf-8')
    for i, question in tqdm(raw_data.values):
        # 预处理:先把问题句子中多余的空格去掉，避免影响判断
        # 比赛数据集特有的，再把'|','$','·'去掉
        question = del_spaces(question).replace(
            '|', '').replace('$', '').replace('·', '')
        # 再把两端多余的空格去掉
        question = question.strip()

        # 符号字符统一
        question = char_unify_convertor(question)

        # 将一些写错的l替换为1
        question = replace_l_with_1(question)

        # 将一些写错的1替换为l
        question = replace_1_with_l(question)

        # 改用封装后的函数，删除拼音音节
        question = rm_pinyin_yinjie(question)

        # 改用封装后的函数，单位表述进行统一
        question = units_mention_unify(question)

        # 改用封装后的函数，超过1个字符的表述替换
        question = convert_some_mentions(question)

        # 将表示比例的中文冒号转为英文冒号
        question = convert_cn_colon_to_en(question)

        # 将英文标点转为中文
        question = convert_en_punct_to_cn(question)

        pred_equation = autosolve.generate(question, topk)
        pred_answer = generate_ans_and_post_process_for_competition_format(
            question, pred_equation)
        fw.write(str(i) + ',' + pred_answer + '\n')
        fw.flush()
    fw.close()


if __name__ == '__main__':

    if model_load_path == '':
        evaluator = Evaluator()
        train_generator = data_generator(train_data, batch_size)

        model.fit_generator(
            train_generator.forfit(),
            steps_per_epoch=len(train_generator),
            epochs=epochs,
            callbacks=[evaluator]
        )
        # 打印模型loss
        with open(loss_log_path, 'a', encoding='utf-8') as f:
            f.write(str(evaluator.losses))
    else:
        model.load_weights(model_load_path)

    # 预测
    predict(test_path, pred_path)
