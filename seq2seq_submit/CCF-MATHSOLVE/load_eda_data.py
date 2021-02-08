import json
import pprint
import random
from string import digits

import numpy as np

from config import operator_no_gt_4, use_eda


def remove_bucket(equation):
    """去掉冗余的括号
    """
    l_buckets, buckets = [], []
    for i, c in enumerate(equation):
        if c == '(':
            l_buckets.append(i)
        elif c == ')':
            buckets.append((l_buckets.pop(), i))
    eval_equation = eval(equation)
    for l, r in buckets:
        new_equation = '%s %s %s' % (
            equation[:l], equation[l + 1:r], equation[r + 1:]
        )
        try:
            if is_equal(eval(new_equation.replace(' ', '')), eval_equation):
                equation = new_equation
        except:
            pass
    return equation.replace(' ', '')


def is_equal(a, b):
    """比较两个结果是否相等
    """
    a = round(float(a), 6)
    b = round(float(b), 6)
    return a == b


def load_train_data(filename):
    D = []  # 获取训练数据
    operators = ['+', '-', '*', '/', '^']
    processed_eda_dict = {}  # 用于track每个问题eda使用了多少

    for f in open(filename):
        data_d = json.loads(f)
        question, equation, answer = data_d['cleaned_text'], data_d['equation'], data_d['ans']

        # 下面设置ues_eda，是为了控制传入的用于控制每个问题使用多少个eda的。
        if use_eda > 0:
            # 大前提：所有原始问题都保留
            if data_d["doc_index_originality"] != 'original':
                # 首次处理某问题的eda
                if data_d["doc_index_originality"] not in processed_eda_dict.keys():
                    processed_eda_dict[data_d["doc_index_originality"]] = 1
                # 非首次处理
                else:
                    # 如果已经得到thresh，则直接舍弃该条数据
                    if processed_eda_dict[data_d["doc_index_originality"]] >= use_eda:
                        continue
                    else:
                        processed_eda_dict[data_d["doc_index_originality"]] += 1
        else:
            # 仅使用原始文本
            if data_d["doc_index_originality"] != 'original':
                continue

        # 考虑将表达式中运算符大于4个的文本不加入训练
        if operator_no_gt_4:
            # counter_all += 1
            counter_operator = 0

        # 初始化找到的分数集合
        fraction_num_set = set()
        # 将segmented_text_new转为列表
        segmented_text_new_list = data_d["segmented_text_new"].split(
            ' ')
        # 遍历segmented_text_new_list列表，发现分数的直接加括号，并将发现的分数添加到上述集合中
        for i_, item in enumerate(segmented_text_new_list):
            if ('/' in item) and (item[0] in digits) and (item[-1] in digits):
                fraction_num_set.add(item)
                segmented_text_new_list[i_] = '({})'.format(item)
        # 将segmented_text_new重新组合成字符串
        data_d["segmented_text_new"] = (
            ' '.join(segmented_text_new_list)).strip()

        print_cond = (len(fraction_num_set) > 0)

        # 将发现的分数集合转成列表，并排序（倒序）
        fraction_num_list = list(fraction_num_set)
        fraction_num_list.sort(key=lambda x: len(x), reverse=True)

        # 如果限制equation中的运算符不超过4个
        if operator_no_gt_4:
            equation_for_filter = data_d["equation"]
            equation_for_filter = equation_for_filter.replace('**', '^')
            # 直接先把分数删掉，因为分数中的/不能算运算符
            for fraction_num in fraction_num_list:
                equation_for_filter = data_d["equation"].replace(
                    fraction_num, '')

            for char in equation_for_filter:
                if char in operators:
                    counter_operator += 1
                else:
                    continue

            # 如果该问题的运算符超过4个，直接舍弃该问题，不加入训练
            if counter_operator > 4:
                # counter_operator_gt_4 += 1
                continue

        # 这里之所以不直接对发现的分数进两端加括号，是为了防止出现，如果题中同时有1/5和11/5，11/5变为(11/5)之后又变为(1(1/5))
        fraction_num_list_ext = []
        for item in fraction_num_list:
            numerator = item.split('/')[0]
            denominator = item.split('/')[1]
            fraction_num_list_ext.append(
                (item, '({}圀/圀{})'.format(numerator, denominator)))

        for fraction_num, fraction_num_ext in fraction_num_list_ext:
            data_d["cleaned_text"] = data_d["cleaned_text"].replace(
                fraction_num, fraction_num_ext)
            data_d["equation"] = data_d["equation"].replace(
                fraction_num, fraction_num_ext)

        # 再把多余的占位符 圀 去掉
        data_d["cleaned_text"] = data_d["cleaned_text"].replace(
            '圀', '')
        data_d["equation"] = data_d["equation"].replace('圀', '')

        # 冒号转除号，剩余百分号处理
        equation = equation.replace(
            '%', '/100').replace('^', '**')  # 将3:4换成3/4，5%换为5/100
        answer = answer.replace('%', '/100')

        if equation[:2] == 'x=':
            equation = equation[2:]
            try:
                if answer == equation:
                    continue
                if is_equal(eval(equation), eval(answer)):
                    D.append((question, remove_bucket(equation), answer))
            except:
                continue
    return D
