import copy
import json
import operator
import pprint
import random
import re
import traceback
from collections import OrderedDict, deque
from copy import deepcopy
from fractions import Fraction
from math import ceil, floor
from string import ascii_letters, digits, punctuation

from sympy import Integer, simplify
from tqdm import tqdm
from treelib import Node, Tree

from src.expressions_transfer import (compute_prefix_expression,
                                      from_infix_to_prefix)

random.seed(42)

priority = {"+": 0, "-": 0, "*": 1, "/": 1, "^": 2}


def parse_and_eval_prefix_expr(prefix_expr_list):

    global priority

    if len(prefix_expr_list) == 0:
        # print('the prefix_expr_list passed in is empty!\n')
        raise Exception('the prefix_expr_list passed in is empty!\n')
    elif prefix_expr_list[0] not in ["+", "-", "*", "/", "^"]:
        if '.' in prefix_expr_list[0]:
            return float(prefix_expr_list[0]), '', f'prefix_expr_list[0] is not an operator, now the prefix_expr_list is: {prefix_expr_list}'
        else:
            return int(prefix_expr_list[0]), '', f'prefix_expr_list[0] is not an operator, now the prefix_expr_list is: {prefix_expr_list}'
    else:
        computed_prefix_expression = compute_prefix_expression(
            prefix_expr_list)

        prefix_expr_list = list(map(lambda x: str(
            float(x[:-1]) / 100) if x.endswith('%') else x, prefix_expr_list))

        tree = Tree()
        op_stack = deque()

        op_stack.append((prefix_expr_list[0], "op_root"))
        tree.create_node(prefix_expr_list[0], "op_root")
        node = tree.get_node("op_root")

        for index_, item in enumerate(prefix_expr_list):
            if index_ == 0:
                pass
            else:

                while len(tree.children(op_stack[-1][1])) >= 2:
                    op_stack.pop()

                if len(tree.children(op_stack[-1][1])) == 0:
                    tree.create_node(
                        (item, 'Left'), f"op_{index_}", parent=op_stack[-1][1], data='Left')
                else:
                    tree.create_node(
                        (item, 'Right'), f"op_{index_}", parent=op_stack[-1][1], data='Right')

                if item in ["+", "-", "*", "/", "^"]:
                    op_stack.append((item, f"op_{index_}"))

        tree_for_infix_expr = deepcopy(tree)

        # for i in range(6):
        while len(tree) > 1:

            for node in tree.all_nodes():
                if node.tag[0] in ["+", "-", "*", "/", "^"] \
                        and len(tree.children(node.identifier)) == 2 \
                        and (tree.children(node.identifier)[0].tag[0] not in ["+", "-", "*", "/", "^"]) \
                        and (tree.children(node.identifier)[1].tag[0] not in ["+", "-", "*", "/", "^"]):

                    operator_raw = node.tag[0]
                    left_or_right = node.data
                    node_id = node.identifier

                    if tree.parent(node_id) is not None:
                        node_parent_id = tree.parent(node_id).identifier
                        operator_parent_raw = tree.parent(node_id).tag[0]
                        operator_parent_raw_priority = priority[operator_parent_raw]
                    else:
                        node_parent_id = operator_parent_raw = None
                        operator_parent_raw_priority = -1

                    operator_raw_priority = priority[operator_raw]

                    # need_brackets = operator_raw_priority <= operator_parent_raw_priority

                    if operator_raw_priority > operator_parent_raw_priority:
                        need_brackets = False
                    elif operator_raw_priority < operator_parent_raw_priority:
                        need_brackets = True
                    elif operator_raw_priority == operator_parent_raw_priority:
                        if operator_raw == '+' or operator_raw == '*':
                            need_brackets = False
                        else:
                            need_brackets = True

                    if tree.children(node.identifier)[0].data == 'Left':
                        operand_left = tree.children(node.identifier)[0].tag[0]
                        operand_right = tree.children(
                            node.identifier)[1].tag[0]

                        operand_left_infix_expr = tree_for_infix_expr.children(node.identifier)[
                            0].tag[0]
                        operand_right_infix_expr = tree_for_infix_expr.children(node.identifier)[
                            1].tag[0]
                    else:
                        operand_left = tree.children(node.identifier)[1].tag[0]
                        operand_right = tree.children(
                            node.identifier)[0].tag[0]

                        operand_left_infix_expr = tree_for_infix_expr.children(node.identifier)[
                            1].tag[0]
                        operand_right_infix_expr = tree_for_infix_expr.children(node.identifier)[
                            0].tag[0]

                    if operand_left.endswith('%'):
                        operand_left = operand_left[:-1]
                        operand_left = f'{eval(operand_left)/100}'

                    if operand_right.endswith('%'):
                        operand_right = operand_right[:-1]
                        operand_right = f'{eval(operand_right)/100}'

                    if int(eval(operand_left)) - eval(operand_left) == 0:
                        operand_left = int(eval(operand_left))
                    else:
                        operand_left = eval(operand_left)

                    if int(eval(operand_right)) - eval(operand_right) == 0:
                        operand_right = int(eval(operand_right))
                    else:
                        operand_right = eval(operand_right)

                    if operator_raw == '+':
                        if need_brackets:
                            node_infix_expr = f'({operand_left_infix_expr}+{operand_right_infix_expr})'
                        else:
                            node_infix_expr = f'{operand_left_infix_expr}+{operand_right_infix_expr}'
                        node_evaluated = operand_left + operand_right
                    elif operator_raw == '-':
                        if need_brackets:
                            node_infix_expr = f'({operand_left_infix_expr}-{operand_right_infix_expr})'
                        else:
                            node_infix_expr = f'{operand_left_infix_expr}-{operand_right_infix_expr}'
                        node_evaluated = operand_left - operand_right
                    elif operator_raw == '*':
                        if need_brackets:
                            node_infix_expr = f'({operand_left_infix_expr}*{operand_right_infix_expr})'
                        else:
                            node_infix_expr = f'{operand_left_infix_expr}*{operand_right_infix_expr}'
                        node_evaluated = operand_left * operand_right
                    elif operator_raw == '/':
                        if need_brackets:
                            node_infix_expr = f'({operand_left_infix_expr}/{operand_right_infix_expr})'
                        else:
                            node_infix_expr = f'{operand_left_infix_expr}/{operand_right_infix_expr}'

                        node_evaluated = operand_left / operand_right
                    elif operator_raw == '^':
                        if need_brackets:
                            node_infix_expr = f'({operand_left_infix_expr}^{operand_right_infix_expr})'
                        else:
                            node_infix_expr = f'{operand_left_infix_expr}^{operand_right_infix_expr}'
                        node_evaluated = operand_left ** operand_right

                    tree_for_infix_expr.remove_node(node_id)
                    tree.remove_node(node_id)

                    if node_parent_id is not None:
                        tree_for_infix_expr.create_node(
                            (f'{node_infix_expr}', left_or_right), node_id, parent=node_parent_id, data=left_or_right)
                        tree.create_node(
                            (f'{node_evaluated}', left_or_right), node_id, parent=node_parent_id, data=left_or_right)
                    else:
                        tree_for_infix_expr.create_node(
                            f'{node_infix_expr}', "op_root")
                        tree.create_node(f'{node_evaluated}', "op_root")

    add_info = ''
    if len(tree.leaves("op_root")) > 1:
        # print(
        #     f'the final tree has multiple leaves, and now the leaves are: {tree.leaves("op_root")}\n')
        raise Exception(
            f'the final tree has multiple leaves, and now the leaves are: {tree.leaves("op_root")}\n')

    if len(tree_for_infix_expr.leaves("op_root")) > 1:
        # print(
        #     f'the final tree_for_infix_expr has multiple leaves, and now the leaves are: {tree_for_infix_expr.leaves("op_root")}\n')
        raise Exception(
            f'the final tree_for_infix_expr has multiple leaves, and now the leaves are: {tree_for_infix_expr.leaves("op_root")}\n')

    if computed_prefix_expression is None:
        add_info = f'the compute_prefix_expression() result is now None, and the parse_and_eval_prefix_expr() result is {tree.leaves("op_root")[0].tag}, and the prefix_expr_list is {prefix_expr_list}\n'
        # print(add_info)
    elif eval(tree.leaves("op_root")[0].tag) - computed_prefix_expression != 0:
        raise Exception(
            f'discrepency found between parse_and_eval_prefix_expr() and compute_prefix_expression(), now the parse_and_eval_prefix_expr() result is {tree.leaves("op_root")[0].tag}, the compute_prefix_expression() result is {computed_prefix_expression}, and the prefix_expr_list is {prefix_expr_list}\n')

    if int(eval(tree.leaves("op_root")[0].tag)) - eval(tree.leaves("op_root")[0].tag) == 0:
        return int(eval(tree.leaves("op_root")[0].tag)), tree_for_infix_expr.leaves("op_root")[0].tag, add_info
    else:
        return eval(tree.leaves("op_root")[0].tag), tree_for_infix_expr.leaves("op_root")[0].tag, add_info


cn_punctuations = '：、「」，。！？【】（）％＃＠＆“”‘’–—−‑——'
cn_punctuations2 = """！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘'‛“”„‟…‧﹏."""
cn_seg_punctuations = '！？｡。，､、〟；'

cn_en_punctuations_set = set(cn_punctuations).union(
    set(cn_punctuations2)).union(set(cn_seg_punctuations)).union(set(punctuation))

# en_seg_punctuations = '!?.,;'

# 小数点不算seg_punctuation，英文句号以．表示 wrong
# 用来断句的，不仅以点为判断依据，还要看点后面是不是数字
# 英文分隔类标点（去除两种点．.，单独判断小数点）
en_seg_punctuations = '!?,;'
# 中英文分隔类标点集合
cn_en_seg_punctuations_set = set(
    cn_seg_punctuations).union(set(en_seg_punctuations))

table_en_punct_to_cn = {ord(f): ord(t) for f, t in zip(
    u',．。!?;',
    u'，。。！？；')}


def convert_en_punct_to_cn(str_):
    return str_.translate(table_en_punct_to_cn)


# 字符统一转换字典
char_unify_dict = {
    '═': '=',
    '﹦': '=',
    '〓': '=',
    '≈': '=',
    '＝': '=',
    '﹖': '?',
    '﹕': ':',
    '∶': ':',
    '︰': ':',
    # 中文冒号处理另见函数convert_cn_colon_to_en()
    # '：': ':',
    '﹢': '+',
    '十': '+',
    '✚': '+',
    '＋': '+',
    '〸': '+',
    '⼗': '+',
    '−': '-',
    '﹣': '-',
    '－': '-',
    '─': '-',
    '×': '*',
    '✖️': '*',
    '╳': '*',
    '∕': '/',
    '∥': '/',
    '⁄': '/',
    '／': '/',
    '÷': '/',
    '〔': '(',
    '〕': ')',
    # TODO 有必要保留大括号类的题目嘛？
    # '{': '(',
    # '}': ')',
    # '﹛': '(',
    # '﹜': ')',
    '【': '(',
    '】': ')',
    '「': '(',
    '」': ')',
    '[': '(',
    ']': ')',
    # '√': '',
    '‘': "'",
    '’': "'",
    '′': "'",
    '“': '"',
    '”': '"',
    '﹑': ',',
    '゜': '°',
    '˚': '°',
    '∘': '°',
    '兀': 'π',
    '兀': 'π',
    'Л': 'π',
    'л': 'π',
    'П': 'π',
    'Ⅱ': 'π',
    '<': '<',
    '>': '>',
    '⋅': '.',
    '•': '·',
    'Ⅴ': 'V',
    'T': 'T',
    'S': 'S',
    '«': '《',
    '»': '》',
    '數': '数',
    '度': '度',
    '不': '不',
    '了': '了',
    'ɡ': 'g',
    '﹟': '#',
    'Ⅰ': 'I',
    'C': 'C',
    '∽': '～',
    '∼': '～',
    '~': '～',
    '—': '～',
    '┅': '…',
    '﹍': '…',
    '⒈': '1',
    '１': '1',
    '２': '2',
    '３': '3',
    '４': '4',
    '５': '5',
    '６': '6',
    '７': '7',
    '８': '8',
    '９': '9',
    '０': '0',
    'у': 'y',
    '％': '%',
}


# 字符统一转换器
def char_unify_convertor(str_):
    for k in char_unify_dict:
        str_ = str_.replace(k, char_unify_dict[k])
    return str_


def convert_cn_colon_to_en(str_):
    str_list = list(str_)
    for i, char in enumerate(str_list):
        if (i > 0) and (i < len(str_list) - 1) and (char == '：') and \
            ((str_list[i-1] in digits) or (str_list[i-1] == '?') or (str_list[i-1] == '？') or (str_list[i-1] == '少') or (str_list[i-1] == '几')) and \
                ((str_list[i+1] in digits) or (str_list[i+1] == '?') or (str_list[i+1] == '？') or (str_list[i+1] == '多') or (str_list[i+1] == '几')):
            str_list[i] = ':'
    return ''.join(str_list)


def del_cn_en_punctuations(str_):
    str_ret = ''
    for i, char in enumerate(str_):
        # 已经包含了去除问题句中的空格
        # +-*/^= 不再删除
        # ．认定为英文句话，都删除
        # .根据情况判断是小数点还是英文句话，是小数点则不删除，否则删除
        if (char == ' ') or (char in cn_en_punctuations_set.difference(set('+-*/^%=().'))) or (char == '．'):
            pass
        elif (char == '.') and ((i == len(str_) - 1) or (i == 0)):
            pass
        elif (char == '.') and (i+1 < len(str_)) and (str_[i+1] in digits) and (i-1 >= 0) and (str_[i-1] in digits):
            str_ret += char
        else:
            str_ret += char
    return str_ret.strip()


# 一些无法解析的unicode字符
unicode_to_rm = [
    '\ue003',
    '\u2005',
    '\u2002',
    '\ue004',
    '\ue00c',
    '\ue008',
    '\ue00b',
    '\u200b',
    '\ue5e5',
    '\u3000',
    '\u00A0',
    '\u0020',
    '\ue005',
    '\uf0b8',
    '\uf0e7',
    '\uf020',
    '\uf02b',
    '\uf0f7',
    '\uf02d',
]


def del_spaces(str_):
    str_ret = ''
    for char in str_:
        if (char == ' ') or (char == '`') or (char in unicode_to_rm) or (char.strip() == ''):
            pass
        else:
            str_ret += char

    # 去除html中的空格标记：
    str_ret = str_ret.replace('&thinsp;', '')
    str_ret = str_ret.replace('&nbsp;', '')
    str_ret = str_ret.replace('&nbip;', '')
    str_ret = str_ret.replace('&ensp;', '')
    str_ret = str_ret.replace('&emsp;', '')
    str_ret = str_ret.replace('&zwnj;', '')
    str_ret = str_ret.replace('&zwj;', '')
    return str_ret.strip()


def filter_all_is_punctuation(str_):
    all_is_punctuation = True
    for char in str_:
        if char not in cn_en_punctuations_set:
            all_is_punctuation = False
            break
    return all_is_punctuation


def sep_by_seg_punctuations(str_):
    list_ret = []
    str_seg = ''

    for i, char in enumerate(str_):
        if char in cn_en_seg_punctuations_set \
                or (char == '．') \
                or ((char == '.') and ((i == len(str_) - 1) or (i == 0))) \
                or ((char == '.') and (not ((i+1 < len(str_)) and (str_[i+1] in digits) and (i-1 >= 0) and (str_[i-1] in digits)))):
            if str_seg != '':
                list_ret.append(str_seg)
                str_seg = ''
        else:
            str_seg += char

    # 循环外再处理一次
    if str_seg != '':
        list_ret.append(str_seg)
        str_seg = ''

    # 去除那些仅由标点（这里考虑的是所有中英文标点，包括，但不限于分隔类标点）组成的成员
    # train.csv:
    # 6480, 化肥厂四月份生产化肥420吨，五月份生产500吨，五月份超产百分之几?______.
    # ['化肥厂四月份生产化肥420吨', '五月份生产500吨', '五月份超产百分之几', '______.']，应将最后一个成员去掉
    list_ret = list(
        filter(lambda x: (not filter_all_is_punctuation(x)), list_ret))

    return list_ret


def convert_mixed_num_to_fraction_competition(str_):
    found_mixed_num_patterns = re.findall(r'(\d+)(_)(\d+/\d+)', str_)
    if len(found_mixed_num_patterns) > 0:
        mixed_num_str_list = list(
            map(lambda x: x[0] + x[1] + x[2], found_mixed_num_patterns))
        fraction_num_list = []
        for mixed_num in found_mixed_num_patterns:
            int_part = int(mixed_num[0])
            denominator_part = int(mixed_num[2].split('/')[1])
            numerator_raw = int(mixed_num[2].split('/')[0])
            numerator_new = int_part * denominator_part + numerator_raw
            fraction_num_list.append(f'{numerator_new}/{denominator_part}')
        return list(zip(mixed_num_str_list, fraction_num_list))
    else:
        return []


def convert_mixed_num_to_fraction_for_graph2tree(str_, from_dataset='competition'):
    # 首先复制给变量question_cleaned
    question_cleaned = str_
    # 生成(带分数，假分数)列表
    if from_dataset == 'competition':
        found_mixed_nums = convert_mixed_num_to_fraction_competition(str_)
    # 如果能生成列表，说明有带分数，则对每个带分数进行替换
    if len(found_mixed_nums) > 0:
        for mixed_num in found_mixed_nums:
            question_cleaned = question_cleaned.replace(
                mixed_num[0], mixed_num[1])
        # print('raw str_: ', str_)
        # print('question_cleaned: ', question_cleaned)
        # print('分数去括号后：', re.sub(r'\((\d+/\d+)\)', '\\1', question_cleaned))
        # print()
    return question_cleaned


def replace_underscore_with_how_much(str_):
    for i in range(20, 1, -1):
        str_ = str_.replace('_' * i, '多少')
    return str_


def convert_some_mentions(str_):
    # 超过1个字符的表述替换
    str_ = str_.replace('((())/(()))', '几分之几')
    str_ = replace_underscore_with_how_much(str_)
    str_ = str_.replace('=多少', '等于多少?')
    str_ = str_.replace('=?', '等于多少?')
    str_ = str_.replace('=？', '等于多少?')
    str_ = str_.replace('﹙ ﹚', '多少')
    str_ = str_.replace('( )', '多少')
    str_ = str_.replace('（ ）', '多少')
    str_ = str_.replace('()', '多少')
    str_ = str_.replace('﹙﹚', '多少')
    str_ = str_.replace('（）', '多少')
    return str_


def round_up(value, keep_float_bits=2):
    # 替换内置round函数,实现默认保留2位小数的精确四舍五入
    return round(value * 10**keep_float_bits) / float(10**keep_float_bits)


def get_add_info(str_):

    # 处理额外信息，如(***)，用作预处理的，还可能是被中文括号包裹
    # 都要考虑：两端都是英文括号的，两端都是中文括号的，左英文右中文的，左中文右英文的

    # 以英文括号结尾，某些结尾可能是【).】【)?】 等等，所以倒数第2个字符是也算
    if str_.endswith(')') or (str_[-2] == ')'):
        reversed_ = str_[::-1]
        try:
            index_ = reversed_.index('(')
        except:
            try:
                index_ = reversed_.index('（')
            except:
                index_ = -1
        if index_ > 0:
            add_info = str_[(0-index_-1):]

        else:
            add_info = None

    # 以中文括号结尾，某些结尾可能是【）。】【）？】 等等，所以倒数第2个字符是也算
    elif str_.endswith('）') or (str_[-2] == '）'):
        reversed_ = str_[::-1]
        try:
            index_ = reversed_.index('（')
        except:
            try:
                index_ = reversed_.index('(')
            except:
                index_ = -1
        if index_ > 0:

            add_info = str_[(0-index_-1):]
        else:
            add_info = None

    else:
        add_info = None

    if add_info is not None:
        if add_info.startswith('(') or add_info.startswith('（'):
            add_info = add_info[1:]
        if add_info.endswith(')') or add_info.endswith('）'):
            add_info = add_info[:-1]
        if len(add_info) >= 2 and (add_info[-2] == ')' or add_info[-2] == '）'):
            add_info = add_info[:-2]
        # if len(add_info) >= 3 and (add_info[-3] == ')' or add_info[-3] == '）'):
        #     add_info = add_info[:-3]
        # question_add_info_set.add(add_info)

    return add_info


# question_add_info_set中每个成员拆成子句
# 列出不应该去掉的，和应该去掉的，比较特征

def keep_add_info(str_):

    # 如果子句中含有下列关键词，则应该去除：
    if ('1个' in str_) \
            or ('1种' in str_) \
            or ('1位' in str_) \
            or ('一位' in str_) \
            or ('2种' in str_) \
            or ('2位' in str_) \
            or ('二位' in str_) \
            or ('两位' in str_) \
            or ('3种' in str_) \
            or ('3位' in str_) \
            or ('三位' in str_) \
            or ('4种' in str_) \
            or ('5种' in str_) \
            or ('6种' in str_) \
            or ('精确' in str_) \
            or ('保留' in str_):
        return False

    # elif ('没有' in str_) or ('不' in str_):
    #     return True

    # 如果子句中含有圆周率有关的，则保留：
    elif ('圆周率' in str_) or ('π' in str_):
        return True

    # 如果子句中含数字、百分号、或英文字符（x除外，因为会作为方程的未知数），则保留：
    else:
        for char in str_:
            if ((char in digits) or (char == '%') or (char in ascii_letters)) \
                    and (char != 'x') \
                    and (char != 'X'):
                return True
    return False


def process_add_info(str_):

    # 获取该条问题需要保留的额外信息字符串
    add_info = get_add_info(str_)
    # 先复制给1个变量：添加了有意义额外信息的问句
    question_with_useful_add_info = str_

    if add_info is not None:

        # 首先删除发现的额外信息
        question_with_useful_add_info = question_with_useful_add_info.replace(
            f'({add_info})', '')
        question_with_useful_add_info = question_with_useful_add_info.replace(
            f'（{add_info}）', '')
        question_with_useful_add_info = question_with_useful_add_info.replace(
            f'（{add_info})', '')
        question_with_useful_add_info = question_with_useful_add_info.replace(
            f'({add_info}）', '')
        question_with_useful_add_info = question_with_useful_add_info.replace(
            add_info, '')

        # 每条额外信息按分隔类标点再拆分成列表（子句）
        question_add_info_list = sep_by_seg_punctuations(add_info)
        # 并按子句长度排序
        question_add_info_list.sort(key=lambda y: len(y), reverse=True)

        # 仅保留有意义的列表（子句）
        question_add_info_list_filtered = list(
            filter(lambda x: keep_add_info(x), question_add_info_list))

        if len(question_add_info_list_filtered) > 0:
            question_with_useful_add_info = question_with_useful_add_info + '(' + \
                '，'.join(question_add_info_list_filtered) + ')'

    return question_with_useful_add_info


# 首先初始化一个单位关键词转换字典（普通字典即可）
# key为待转换的单位关键词
# value为转换后的单位关键词
units_mention_unified = dict()

# 长度类关键词
units_mention_unified['km'] = '千米'
units_mention_unified['㎞'] = '千米'
units_mention_unified['公里'] = '千米'
units_mention_unified['dm'] = '分米'
units_mention_unified['cm'] = '厘米'
units_mention_unified['㎝'] = '厘米'
units_mention_unified['mm'] = '毫米'
units_mention_unified['㎜'] = '毫米'
units_mention_unified['m'] = '米'

# 面积类关键词
units_mention_unified['km^2'] = '平方千米'
units_mention_unified['km**2'] = '平方千米'
units_mention_unified['km2'] = '平方千米'
units_mention_unified['km²'] = '平方千米'
units_mention_unified['㎢'] = '平方千米'
units_mention_unified['平方公里'] = '平方千米'
units_mention_unified['公里²'] = '平方千米'
units_mention_unified['k㎡'] = '平方千米'
units_mention_unified['千米²'] = '平方千米'
units_mention_unified['k米²'] = '平方千米'
units_mention_unified['千米**2'] = '平方千米'
units_mention_unified['公里**2'] = '平方千米'
units_mention_unified['dm^2'] = '平方分米'
units_mention_unified['dm**2'] = '平方分米'
units_mention_unified['dm2'] = '平方分米'
units_mention_unified['dm²'] = '平方分米'
units_mention_unified['d米²'] = '平方分米'
units_mention_unified['d㎡'] = '平方分米'
units_mention_unified['分米²'] = '平方分米'
units_mention_unified['分米**2'] = '平方分米'
units_mention_unified['cm^2'] = '平方厘米'
units_mention_unified['cm**2'] = '平方厘米'
units_mention_unified['cm2'] = '平方厘米'
units_mention_unified['cm²'] = '平方厘米'
units_mention_unified['c㎡'] = '平方厘米'
units_mention_unified['㎠'] = '平方厘米'
units_mention_unified['c米²'] = '平方厘米'
units_mention_unified['厘米²'] = '平方厘米'
units_mention_unified['厘米**2'] = '平方厘米'
units_mention_unified['mm^2'] = '平方毫米'
units_mention_unified['mm**2'] = '平方毫米'
units_mention_unified['mm2'] = '平方毫米'
units_mention_unified['mm²'] = '平方毫米'
units_mention_unified['m㎡'] = '平方毫米'
units_mention_unified['㎟'] = '平方毫米'
units_mention_unified['毫米²'] = '平方毫米'
units_mention_unified['m^2'] = '平方米'
units_mention_unified['m米²'] = '平方毫米'
units_mention_unified['毫米**2'] = '平方毫米'
units_mention_unified['m**2'] = '平方米'
units_mention_unified['m2'] = '平方米'
units_mention_unified['m²'] = '平方米'
units_mention_unified['㎡'] = '平方米'
units_mention_unified['米²'] = '平方米'
units_mention_unified['米**2'] = '平方米'


# 体积类关键词
units_mention_unified['dm^3'] = '立方分米'
units_mention_unified['dm**3'] = '立方分米'
units_mention_unified['dm3'] = '立方分米'
units_mention_unified['dm³'] = '立方分米'
units_mention_unified['d㎥'] = '立方分米'
units_mention_unified['分米³'] = '立方分米'
units_mention_unified['d米³'] = '立方分米'
units_mention_unified['分米**3'] = '立方分米'
units_mention_unified['cm^3'] = '立方厘米'
units_mention_unified['cm**3'] = '立方厘米'
units_mention_unified['cm3'] = '立方厘米'
units_mention_unified['cm³'] = '立方厘米'
units_mention_unified['c㎥'] = '立方厘米'
units_mention_unified['㎤'] = '立方厘米'
units_mention_unified['厘米³'] = '立方厘米'
units_mention_unified['c米³'] = '立方厘米'
units_mention_unified['厘米**3'] = '立方厘米'
units_mention_unified['mm^3'] = '立方毫米'
units_mention_unified['mm**3'] = '立方毫米'
units_mention_unified['mm3'] = '立方毫米'
units_mention_unified['mm³'] = '立方毫米'
units_mention_unified['m㎥'] = '立方毫米'
units_mention_unified['㎣'] = '立方毫米'
units_mention_unified['毫米³'] = '立方毫米'
units_mention_unified['m米³'] = '立方毫米'
units_mention_unified['毫米**3'] = '立方毫米'
units_mention_unified['m^3'] = '立方米'
units_mention_unified['m**3'] = '立方米'
units_mention_unified['m3'] = '立方米'
units_mention_unified['m³'] = '立方米'
units_mention_unified['米³'] = '立方米'
units_mention_unified['㎥'] = '立方米'
units_mention_unified['米**3'] = '立方米'
units_mention_unified['多少方'] = '多少立方米'
units_mention_unified['几方'] = '几立方米'
units_mention_unified['?方'] = '多少立方米'
units_mention_unified['？方'] = '多少立方米'

# 容积类关键词
units_mention_unified['l'] = '升'
units_mention_unified['L'] = '升'
units_mention_unified['ml'] = '毫升'
units_mention_unified['mL'] = '毫升'

# 重量类关键词
units_mention_unified['t'] = '吨'
units_mention_unified['kg'] = '千克'
units_mention_unified['Kg'] = '千克'
units_mention_unified['KG'] = '千克'
units_mention_unified['㎏'] = '千克'
units_mention_unified['公斤'] = '千克'
units_mention_unified['g'] = '克'
units_mention_unified['mg'] = '毫克'

# 圆周率类关键词
units_mention_unified['π'] = '圆周率'
units_mention_unified['pi'] = '圆周率'
units_mention_unified['PI'] = '圆周率'
units_mention_unified['Pi'] = '圆周率'
# 上面的单位表述转换中已经做过，此处不再做
# units_mention_unified['兀'] = '圆周率'
# units_mention_unified['Л'] = '圆周率'
# units_mention_unified['л'] = '圆周率'

units_mention_unified['r'] = '半径'
# units_mention_unified['R'] = '半径' # test.csv 5893 R2线
# units_mention_unified['d'] = '直径'
# units_mention_unified['D'] = '直径' # test.csv 6097 3D电影

# 时间类关键词
units_mention_unified['h'] = '小时'
# 区别于上面的 米
units_mention_unified['/m'] = '/分钟'
units_mention_unified['s'] = '秒钟'

# 温度类关键词
units_mention_unified['℃'] = '摄氏度'
units_mention_unified['℉'] = '华氏度'
units_mention_unified['**0C'] = '摄氏度'
units_mention_unified['**0F'] = '华氏度'

units_mention_unified['千瓦·时'] = '度'
# units_mention_unified['六·一'] = '六一'
# units_mention_unified['五·一'] = '五一'
# units_mention_unified['十·一'] = '十一'
# units_mention_unified['七·一'] = '七一'
# units_mention_unified['八·一'] = '八一'


# 对待转换的关键词，根据其长度进行排序，越长越靠前，因为越长则特指性越强，应优先替换
# 如：cm应替换成“厘米”，而不是将其中的m替换成“米”
keys = sorted(units_mention_unified.keys(),
              key=lambda x: len(x), reverse=True)

# 初始化一个有序字典
units_mention_unified_ordered = OrderedDict()
# 依据上面排好序的key，重新构造一个有序字典，用于问题中的单位转换
for key in keys:
    units_mention_unified_ordered[key] = units_mention_unified[key]


def units_mention_unify(str_):
    # 将处理干净的问题文本复制给1个变量：已做单位统一替换的（真）
    question_with_units_unified = str_
    # 遍历单位转换（有序）字典
    for k in units_mention_unified_ordered:
        # 发现了需要转换的单位
        if k in str_:
            # 真正的替换
            question_with_units_unified = question_with_units_unified.replace(
                k, units_mention_unified_ordered[k])
    return question_with_units_unified


# 文本预处理还要加一条：
# l右边是小数点、冒号（表示比例）、百分号、单位词或者数字的，
# 或者左边不是数字的，
# 将l化为1，
# 如：
# train.csv:
# 97,把l0克盐放在190克水中，盐水的含盐率是多少？,5%
# 597,建筑工地运来一堆水泥，用去l25吨后，剩下的比这批水泥的25%少5吨，这批水泥共多少吨?,160
# 813,鸡兔同笼共47只，脚有l00只，鸡有多少只?,44
# 1047,甲、乙两个运输队分别接受运同样多货物的任务，他们各工作l4天后，甲队剩下64吨没运，乙队剩下484吨没运，已知乙队效率是甲队的60%，甲队每天运多少吨?,75
# 2622,小明看一本故事书，已经看了24页，剩下的每天看6页，l4天看完，这本故事书一共有多少页?,108
# 5346,红星机械厂加工一批零件，经检验发现：李师傅的次品个数与所做零件总个数的比是2:25，张师傅的次品个数与合格品个数的比是l:19.他们的合格率各是多少?,92%
# 7420,李老师发表一篇文章，稿费是1500元．为此她要将超过800的部分按l4%的税率缴纳个人所得税．她应缴税多少元．,98
# 10334,美术课上，老师用2/3张彩纸折了6只纸鹤，要折l00只纸鹤，共需多少张这样的彩纸?,12
# 10494,"甲、乙两地相距l56千米,一辆轿车行驶全程的3/8用了2/3小时，按这样的速度计算，轿车行完全程需多少时间?",179
# 11796,一个长方形花坛，长3米，是宽的l.5倍，里面种着30棵月季，平均每棵月季占地多少平方米?,0.2

# test.csv:
# 954,园林工人沿公路一侧植树，每隔6米种一棵，一共种100棵，从第l棵到最后一棵的距离是多少米？
# 1136,2010年5月l韪，上海世博会正式开幕.5月14日首次达到单日入园人数大约24.04万人，然而5月l5日单日入园人数创新高，比5月l4日单日入园人数还多25%，5月15日单日入园人数是多少万人?
# 1367,A型载重车有8个轮子，B型载重车有12个轮子，现有这两种载重车l7辆，共有172个轮子，求A型车有多少辆?
# 2481,个体户小王承接了建筑公司一项运输2000块玻璃的业务，并签订了合同。合同上规定：每块玻璃运费1.2元；如果运输过程中有损坏，每损坏一块，除了要扣除l.2元的运输费外，还要赔偿6.7元。小王把这2000块玻璃运送到指定地点后，建筑公司按合同付给他2005元。运输过程中损坏了多少块玻璃?
# 3048,学校买回6箱墨水，每箱l2瓶，一共用去了576元，平均每瓶墨水多少元?
# 3052,一辆汽车从总站开出，全车座位上有20%空位，到A站有l2人下车，20人上车，这时车内的座位恰好坐满。这辆车共有多少个座位?
# 4235,一块菜地是一个等腰梯形，它的上底长l2米，下底长16米，腰长7米。如果在菜地四周围上篱笆，篱笆长多少米?
# 4256,妈妈和办公室的同事共l2人聚餐，一共消费403.2元，如果采用AA制消费，每个人应付多少元？（AA制是指：各人平均分担所需费用．）
# 4393,妈妈到超市买了2.5千克黄瓜，交给售货员l0元，找回2元，每千克黄瓜多少元?
# 4568,半径为l0厘米的圆，其面积是多少平方厘米？
# 4624,已知扇形的圆心角为l20度，半径为3，则这个扇形的面积是多少？
# 4667,一个圆形花园的直径是6米，在它周围有一条宽l米的环形鹅卵石小路。这条小路的面积是多少平方米?
# 4797,直径为l8cm的圆中，圆心角40°．的扇形面积是多少？
# 5743,有一袋米，第一次取出它的40%，第二次比第一次多取3千克，还剩下l5千克。原来这袋米重多少千克?
# 5775,造纸厂去年前七个月完成全年计划的75%，后五个月又生产了l600吨，正好完成任务，若要超产全年计划的l0%，还需生产多少吨?
# 5852,水果店运来l8筐梨和15筐苹果，一共重735千克，每筐梨重20千克，每筐苹果重多少千克?
# 6669,一个合唱队有84人，合唱队的人数比舞蹈队人数的3倍多l5人，舞蹈队有多少人？
# 6963,"一个长l0分米,宽8分米,高6分米的长方体,它的表面积是平方分米"


def replace_l_with_1(str_):
    str_list = list(str_)
    for i, char in enumerate(str_list):
        if ((char == 'l') and (i+1 < len(str_) and ((str_[i+1] in digits) or (str_[i+1] == '.') or (str_[i+1] == ':') or (str_[i+1] == '：') or (str_[i+1] == '%') or (str_[i+1] in units_mention_unified_ordered.keys()) or (str_[i+1] in units_mention_unified_ordered.values())))) \
                or ((char == 'l') and ((i-1 >= 0) and (str_[i-1] not in digits))):
            str_list[i] = '1'
    return ''.join(str_list)


# 未注音和带注音的韵母表列表
yunmu_with_zhuyin_ext = [
    'a', 'ā', 'á', 'ǎ', 'à',
    'o', 'ō', 'ó', 'ǒ', 'ò',
    'e', 'ē', 'é', 'ě', 'è',
    'i', 'ī', 'í', 'ǐ', 'ì',
    'u', 'ū', 'ú', 'ǔ', 'ù',
    'ü', 'ǖ', 'ǘ', 'ǚ', 'ǜ',
]


def replace_1_with_l(str_):
    str_list = list(str_)
    for i, char in enumerate(str_list):
        if (char == '1') and (i+1 < len(str_)) and (str_[i+1] in yunmu_with_zhuyin_ext):
            str_list[i] = 'l'
    return ''.join(str_list)


# 带注音的韵母表列表
yunmu_with_zhuyin_list = [
    'ā', 'á', 'ǎ', 'à',
    'ō', 'ó', 'ǒ', 'ò',
    'ē', 'é', 'ě', 'è',
    'ī', 'í', 'ǐ', 'ì',
    'ū', 'ú', 'ǔ', 'ù',
    'ǖ', 'ǘ', 'ǚ', 'ǜ',
]

# 初始化一个韵母及其注音的有序字典
yunmu_with_zhuyin_ordered_dict = OrderedDict()
# 按每个韵母的注音优先级顺序 a > o > e > i > u > ü，逐个添加每个韵母的4声注音
yunmu_with_zhuyin_ordered_dict['a'] = ['ā', 'á', 'ǎ', 'à']
yunmu_with_zhuyin_ordered_dict['o'] = ['ō', 'ó', 'ǒ', 'ò']
yunmu_with_zhuyin_ordered_dict['e'] = ['ē', 'é', 'ě', 'è']
yunmu_with_zhuyin_ordered_dict['i'] = ['ī', 'í', 'ǐ', 'ì']
yunmu_with_zhuyin_ordered_dict['u'] = ['ū', 'ú', 'ǔ', 'ù']
yunmu_with_zhuyin_ordered_dict['ü'] = ['ǖ', 'ǘ', 'ǚ', 'ǜ']

# 原始音节表（所有声母+韵母组合），摘自 https://baike.baidu.com/item/%E6%8B%BC%E9%9F%B3%E5%AD%97%E6%AF%8D%E8%A1%A8/5428784?fr=aladdin#1
yinjie_table = [
    'ba', 'bo', 'bai', 'bei', 'bao', 'ban', 'ben', 'bang', 'beng', 'bi', 'bie', 'biao', 'bian', 'bin', 'bing', 'bu',
    'pa', 'po', 'pai', 'pao', 'pou', 'pan', 'pen', 'pei', 'pang', 'peng', 'pi', 'pie', 'piao', 'pian', 'pin', 'ping', 'pu',
    'ma', 'mo', 'me', 'mai', 'mao', 'mou', 'man', 'men', 'mei', 'mang', 'meng', 'mi', 'mie', 'miao', 'miu', 'mian', 'min', 'ming', 'mu',
    'fa', 'fo', 'fei', 'fou', 'fan', 'fen', 'fang', 'feng', 'fu',
    'da', 'de', 'dai', 'dei', 'dao', 'dou', 'dan', 'dang', 'den', 'deng', 'di', 'die', 'diao', 'diu', 'dian', 'ding', 'dong', 'du', 'duan', 'dun', 'dui', 'duo',
    'ta', 'te', 'tai', 'tao', 'tou', 'tan', 'tang', 'teng', 'ti', 'tie', 'tiao', 'tian', 'ting', 'tong', 'tu', 'tuan', 'tun', 'tui', 'tuo',
    'na', 'nai', 'nei', 'nao', 'ne', 'nen', 'nan', 'nang', 'neng', 'ni', 'nie', 'niao', 'niu', 'nian', 'nin', 'niang', 'ning', 'nong', 'nou', 'nu', 'nuan', 'nun', 'nuo', 'nü', 'nüe',
    'la', 'le', 'lo', 'lai', 'lei', 'lao', 'lou', 'lan', 'lang', 'leng', 'li', 'lia', 'lie', 'liao', 'liu', 'lian', 'lin', 'liang', 'ling', 'long', 'lu', 'luo', 'lou', 'luan', 'lun', 'lü', 'lüe',
    'ga', 'ge', 'gai', 'gei', 'gao', 'gou', 'gan', 'gen', 'gang', 'geng', 'gong', 'gu', 'gua', 'guai', 'guan', 'guang', 'gui', 'guo',
    'ka', 'ke', 'kai', 'kao', 'kou', 'kan', 'ken', 'kang', 'keng', 'kong', 'ku', 'kua', 'kuai', 'kuan', 'kuang', 'kui', 'kun', 'kuo',
    'ha', 'he', 'hai', 'han', 'hei', 'hao', 'hou', 'hen', 'hang', 'heng', 'hong', 'hu', 'hua', 'huai', 'huan', 'hui', 'huo', 'hun', 'huang',
    'ji', 'jia', 'jie', 'jiao', 'jiu', 'jian', 'jin', 'jiang', 'jing', 'jiong', 'ju', 'juan', 'jun', 'jue',
    'qi', 'qia', 'qie', 'qiao', 'qiu', 'qian', 'qin', 'qiang', 'qing', 'qiong', 'qu', 'quan', 'qun', 'que',
    'xi', 'xia', 'xie', 'xiao', 'xiu', 'xian', 'xin', 'xiang', 'xing', 'xiong', 'xu', 'xuan', 'xun', 'xue',
    'zha', 'zhe', 'zhi', 'zhai', 'zhao', 'zhou', 'zhan', 'zhen', 'zhang', 'zheng', 'zhong', 'zhu', 'zhua', 'zhuai', 'zhuan', 'zhuang', 'zhun', 'zhui', 'zhuo',
    'cha', 'che', 'chi', 'chai', 'chao', 'chou', 'chan', 'chen', 'chang', 'cheng', 'chong', 'chu', 'chua', 'chuai', 'chuan', 'chuang', 'chun', 'chui', 'chuo',
    'sha', 'she', 'shi', 'shai', 'shao', 'shou', 'shan', 'shen', 'shang', 'sheng', 'shu', 'shua', 'shuai', 'shuan', 'shuang', 'shun', 'shui', 'shuo',
    're', 'ri', 'rao', 'rou', 'ran', 'ren', 'rang', 'reng', 'rong', 'ru', 'ruan', 'run', 'ruo',
    'za', 'ze', 'zi', 'zai', 'zao', 'zan', 'zou', 'zang', 'zei', 'zen', 'zeng', 'zong', 'zu', 'zuan', 'zun', 'zui', 'zuo',
    'ca', 'ce', 'ci', 'cai', 'cao', 'cou', 'can', 'cen', 'cang', 'ceng', 'cong', 'cu', 'cuan', 'cun', 'cui', 'cuo',
    'sa', 'se', 'si', 'sai', 'sao', 'sou', 'san', 'sen', 'sang', 'seng', 'song', 'su', 'suan', 'sun', 'sui', 'suo',
    'ya', 'yao', 'you', 'yan', 'yang', 'yu', 'ye', 'yue', 'yuan', 'yi', 'yin', 'yun', 'ying', 'yo', 'yong',
    'wa', 'wo', 'wai', 'wei', 'wan', 'wen', 'wang', 'weng', 'wu',
]

# 初始化一个空列表，作为带注音的音节表
yinjie_table_with_zhuyin = []

# 遍历原始音节表
for yinjie in yinjie_table:
    # 按注音优先级顺序遍历韵母
    for yunmu in yunmu_with_zhuyin_ordered_dict:
        if yunmu in yinjie:
            # 首先添加原始音节（未注音）
            # 不再添加
            # yinjie_table_with_zhuyin.append(yinjie)
            # 再添加4声注音，和4声注音的每个首字母大写形式
            for yunmu_with_zhuyin in yunmu_with_zhuyin_ordered_dict[yunmu]:
                yinjie_table_with_zhuyin.append(
                    yinjie.replace(yunmu, yunmu_with_zhuyin))
                yinjie_table_with_zhuyin.append(
                    yinjie.replace(yunmu, yunmu_with_zhuyin).capitalize())
            # 已在优先级最高的韵母上完成注音，直接break，之后开始处理下一个音节
            break

# 注音音节表的长度应是原始音节表的5倍（未注音 + 4声注音）
# 注音音节表的长度应是原始音节表的4倍（4声注音 + 每个音节首字母大写形式）
assert len(yinjie_table_with_zhuyin) == 4 * 2 * len(yinjie_table)


# 同样要对生成带注音音节表按每个成员的字符串长度排个序，因为长度越长，特指性越强，应优先匹配：
yinjie_table_with_zhuyin.sort(key=lambda x: len(x), reverse=True)


def rm_pinyin_yinjie(str_):
    # 每个问题首先假定没有拼音，初始化一个空的集合found_yinjie_set
    found_yinjie_set = set()
    # 将处理干净的问题文本复制给1个变量：删除拼音的文本
    question_with_yinjie_deleted = str_
    # 为提高性能，采用两层遍历，外层先遍历韵母，有韵母的才有可能是拼音：
    for yunmu in yunmu_with_zhuyin_list:
        if yunmu in str_:
            # 有韵母的再遍历带注音的音节表：
            for yinjie in yinjie_table_with_zhuyin:
                if yinjie in str_:
                    # 将找到的音节添加到该问题的音节集合中
                    found_yinjie_set.add(yinjie)
        # 没有韵母的直接pass
        else:
            pass

    # 如果该问题的音节集合有成员，则发现了拼音音节：
    if len(found_yinjie_set) > 0:
        found_yinjie_list = list(found_yinjie_set)
        # 同样首先要先按每个找到的音节字符串长短排序，越长（特指性越强）越靠前，需要优先匹配并替换
        found_yinjie_list.sort(key=lambda x: len(x), reverse=True)
        # 对发现的音节逐pattern去除：
        for yinjie in found_yinjie_list:

            # 两端英文括号
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                f'({yinjie})', '')
            # 两端中文括号
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                f'（{yinjie}）', '')
            # 左英右中
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                f'({yinjie}）', '')
            # 左中右英
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                f'（{yinjie})', '')
            # 左英
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                f'({yinjie}', '')
            # 左中
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                f'（{yinjie}', '')
            # 右英
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                f'{yinjie})', '')
            # 右中
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                f'{yinjie}）', '')
            # 原始
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                yinjie, '')

    return question_with_yinjie_deleted


def contains_cn_chars(str_):
    contains = False
    for char in str_:
        if '\u4e00' <= char <= '\u9fff':
            contains = True
            break
    return contains


def contains_non_legal_ans_chars(str_):
    contains = False
    for char in str_:
        if (char in digits) or (char == '.') or (char == '%') or (char == '/'):
            pass
        else:
            contains = True
            break
    return contains


# 识别的外面带括号的分数替换字符
fraction_num_keys_br = ['🄲', '🄳', '🄴', '🄵', '🄶',
                        '🄷', '🄸', '🄹', '🄺', '🄻', '🄼', '🄽', '🄾', '🄿']

# 识别的分数替换字符
fraction_num_keys = ['⑧', '⑨', '⑩', '⑪', '⑫',
                     '⑬', '⑭', 'Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ', 'Ⓔ', 'Ⓕ', 'Ⓖ']

# 识别的小数百分数替换字符
percentage_float_keys = ['⑮', '⑯', '⑰', '⑱', '⑲',
                         '⑳', '㉑', 'Ⓗ', 'Ⓘ', 'Ⓙ', 'Ⓚ', 'Ⓛ', 'Ⓜ︎', 'Ⓝ']

# 识别的整数百分数替换字符
percentage_int_keys = ['㉒', '㉓', '㉔', '㉕', '㉖',
                       '㉗', '㉘', 'Ⓞ', 'Ⓟ', 'Ⓠ', 'Ⓡ', 'Ⓢ', 'Ⓣ', 'Ⓤ']

# 识别的小数替换字符 TODO 注意 A B 替换了原来的 a b，group_num可能要重跑
float_num_keys = ['㉙', '㉚', '㉛', '㉜', '㉝', '㉞',
                  '㉟', 'Ⓥ', 'Ⓦ', 'Ⓧ', 'Ⓨ', 'Ⓩ', '🄰', '🄱']

# 识别的整数替换字符
int_num_keys = ['㊱', '㊲', '㊳', '㊴', '㊵', '㊶',
                '㊷', '㊸', '㊹', '㊺', '㊻', '㊼', '㊽', '㊾', '㊿']

# 以上合并成一个列表
num_keys_list = fraction_num_keys + percentage_float_keys + \
    percentage_int_keys + float_num_keys + int_num_keys + fraction_num_keys_br

# 分词的时候以下单位的提及均作为整体，不分开
units_list = [
    '千米',
    '分米',
    '厘米',
    '毫米',
    '平方千米',
    '平方分米',
    '平方厘米',
    '平方毫米',
    '平方米',
    '立方分米',
    '立方厘米',
    '立方毫米',
    '立方米',
    '毫升',
    '千克',
    '毫克',
    '圆周率',
    '半径',
    '直径',
    '周长',
    '边长',
    '摄氏度',
    '华氏度',
    '千米/时',
    '千米/小时',
    '千米/分',
    '千米/分钟',
    '千米/秒',
    '千米/秒钟',
    '米/时',
    '米/小时',
    '米/分',
    '米/分钟',
    '米/秒',
    '米/秒钟',
]


def generate_num_list(str_, for_scraper=False):

    if for_scraper:
        # 带分数匹配列表，不必构造字典，直接将发现的带分数化为假分数，然后走后续分数匹配流程
        # 这里之所以假定zybang中的带分数格式为1(2/3)，是因为在对爬取的结果的计算过程中的分数进行替换的时候，外面加上了括号，
        # 如果前面再有整数，就是带分数，那么就会变成上面那种格式
        pattern_mixed_num = re.findall(r'(\d+)\((\d+/\d+)\)', str_)
        if len(pattern_mixed_num) > 0:
            # 排序（降序）：字符串越长，特指性越强，应优先匹配/替换
            pattern_mixed_num.sort(key=lambda x: len(x), reverse=True)

            for i, mixed_num in enumerate(pattern_mixed_num):

                int_part = int(mixed_num[0])
                denominator_part = int(mixed_num[1].split('/')[1])
                numerator_raw = int(mixed_num[1].split('/')[0])
                numerator_new = int_part * denominator_part + numerator_raw
                str_ = str_.replace(
                    f'{int_part}({numerator_raw}/{denominator_part})', f'{numerator_new}/{denominator_part}')

    if for_scraper:
        # 分数匹配列表，先匹配外面带括号的分数，后面不带括号的分数后续流程会匹配到
        pattern_fraction_br = re.findall(r'(\(\d+/\d+\))', str_)

        if len(pattern_fraction_br) > 0:
            # 排序（降序）：字符串越长，特指性越强，应优先匹配/替换
            pattern_fraction_br.sort(key=lambda x: len(x), reverse=True)
            fraction_num_keys_br_consumed = []
            for i, fraction in enumerate(pattern_fraction_br):
                str_ = str_.replace(fraction, fraction_num_keys_br[i])
                fraction_num_keys_br_consumed.append(fraction_num_keys_br[i])
            # 构造该问题中分数-字符转换字典
            fraction_key_num_pairs_br = dict(
                zip(fraction_num_keys_br_consumed, pattern_fraction_br))
            # pprint.pprint(fraction_key_num_pairs_br)
        else:
            fraction_key_num_pairs_br = dict()

    # 分数匹配列表
    pattern_fraction = re.findall(r'(\d+/\d+)', str_)

    if len(pattern_fraction) > 0:
        # 排序（降序）：字符串越长，特指性越强，应优先匹配/替换
        pattern_fraction.sort(key=lambda x: len(x), reverse=True)
        fraction_num_keys_consumed = []
        for i, fraction in enumerate(pattern_fraction):
            str_ = str_.replace(fraction, fraction_num_keys[i])
            fraction_num_keys_consumed.append(fraction_num_keys[i])
        # 构造该问题中分数-字符转换字典
        fraction_key_num_pairs = dict(
            zip(fraction_num_keys_consumed, pattern_fraction))
    else:
        fraction_key_num_pairs = dict()

    # 小数百分数匹配列表
    pattern_percentage_float = re.findall(r'(\d+\.\d+%)', str_)

    if len(pattern_percentage_float) > 0:
        pattern_percentage_float.sort(
            key=lambda x: len(x), reverse=True)
        percentage_float_keys_consumed = []
        for i, percentage_float in enumerate(pattern_percentage_float):
            str_ = str_.replace(
                percentage_float, percentage_float_keys[i])
            percentage_float_keys_consumed.append(
                percentage_float_keys[i])
        percentage_float_key_num_pairs = dict(
            zip(percentage_float_keys_consumed, pattern_percentage_float))
    else:
        percentage_float_key_num_pairs = dict()

    # 整数百分数匹配列表
    pattern_percentage_int = re.findall(r'(\d+%)', str_)

    if len(pattern_percentage_int) > 0:
        pattern_percentage_int.sort(key=lambda x: len(x), reverse=True)
        percentage_int_keys_consumed = []
        for i, percentage_int in enumerate(pattern_percentage_int):
            str_ = str_.replace(
                percentage_int, percentage_int_keys[i])
            percentage_int_keys_consumed.append(
                percentage_int_keys[i])
        percentage_int_key_num_pairs = dict(
            zip(percentage_int_keys_consumed, pattern_percentage_int))
    else:
        percentage_int_key_num_pairs = dict()

    # 小数匹配列表
    pattern_float = re.findall(r'(\d+\.\d+)', str_)

    if len(pattern_float) > 0:
        pattern_float.sort(key=lambda x: len(x), reverse=True)
        float_keys_consumed = []
        for i, float_ in enumerate(pattern_float):
            str_ = str_.replace(float_, float_num_keys[i])
            float_keys_consumed.append(float_num_keys[i])
        float_key_num_pairs = dict(
            zip(float_keys_consumed, pattern_float))
    else:
        float_key_num_pairs = dict()

    # 整数匹配列表
    pattern_int = re.findall(r'(\d+)', str_)

    if len(pattern_int) > 0:
        pattern_int.sort(key=lambda x: len(x), reverse=True)
        int_keys_consumed = []
        for i, int_ in enumerate(pattern_int):
            str_ = str_.replace(int_, int_num_keys[i])
            int_keys_consumed.append(int_num_keys[i])
        int_key_num_pairs = dict(
            zip(int_keys_consumed, pattern_int))

    else:
        int_key_num_pairs = dict()

    num_list = []
    # 按顺序遍历问题中的替换字符，并按出现顺序生成num_list
    for char in str_:
        if char in num_keys_list:
            num_list.append(char)

    if for_scraper:
        if len(pattern_fraction_br) > 0:
            num_list = list(map(
                lambda x: fraction_key_num_pairs_br[x][1:-1] if x in fraction_key_num_pairs_br.keys() else x, num_list))
            # pprint.pprint(num_list)

    if len(pattern_fraction) > 0:
        num_list = list(map(
            lambda x: fraction_key_num_pairs[x] if x in fraction_key_num_pairs.keys() else x, num_list))
    if len(pattern_percentage_float) > 0:
        num_list = list(map(
            lambda x: percentage_float_key_num_pairs[x] if x in percentage_float_key_num_pairs.keys() else x, num_list))
    if len(pattern_percentage_int) > 0:
        num_list = list(map(
            lambda x: percentage_int_key_num_pairs[x] if x in percentage_int_key_num_pairs.keys() else x, num_list))
    if len(pattern_float) > 0:
        num_list = list(map(
            lambda x: float_key_num_pairs[x] if x in float_key_num_pairs.keys() else x, num_list))
    if len(pattern_int) > 0:
        num_list = list(map(
            lambda x: int_key_num_pairs[x] if x in int_key_num_pairs.keys() else x, num_list))

    if for_scraper:
        return {
            'num_list': num_list,
            'pattern_fraction_br': pattern_fraction_br,
            'pattern_fraction': pattern_fraction,
            'fraction_key_num_pairs': fraction_key_num_pairs,
            'pattern_percentage_float': pattern_percentage_float,
            'percentage_float_key_num_pairs': percentage_float_key_num_pairs,
            'pattern_percentage_int': pattern_percentage_int,
            'percentage_int_key_num_pairs': percentage_int_key_num_pairs,
            'pattern_float': pattern_float,
            'float_key_num_pairs': float_key_num_pairs,
            'pattern_int': pattern_int,
            'int_key_num_pairs': int_key_num_pairs,
            'question_num_replaced': str_,
        }
    else:
        return {
            'num_list': num_list,
            'pattern_fraction': pattern_fraction,
            'fraction_key_num_pairs': fraction_key_num_pairs,
            'pattern_percentage_float': pattern_percentage_float,
            'percentage_float_key_num_pairs': percentage_float_key_num_pairs,
            'pattern_percentage_int': pattern_percentage_int,
            'percentage_int_key_num_pairs': percentage_int_key_num_pairs,
            'pattern_float': pattern_float,
            'float_key_num_pairs': float_key_num_pairs,
            'pattern_int': pattern_int,
            'int_key_num_pairs': int_key_num_pairs,
            'question_num_replaced': str_,
        }


def revert_back_to_num(segmented_text_list, args_dict):
    pattern_fraction = args_dict['pattern_fraction']
    fraction_key_num_pairs = args_dict['fraction_key_num_pairs']
    pattern_percentage_float = args_dict['pattern_percentage_float']
    percentage_float_key_num_pairs = args_dict['percentage_float_key_num_pairs']
    pattern_percentage_int = args_dict['pattern_percentage_int']
    percentage_int_key_num_pairs = args_dict['percentage_int_key_num_pairs']
    pattern_float = args_dict['pattern_float']
    float_key_num_pairs = args_dict['float_key_num_pairs']
    pattern_int = args_dict['pattern_int']
    int_key_num_pairs = args_dict['int_key_num_pairs']

    # 分完词后再把字符替换回数字
    if len(pattern_fraction) > 0:
        segmented_text_list = list(map(
            lambda x: fraction_key_num_pairs[x] if x in fraction_key_num_pairs.keys() else x, segmented_text_list))
    if len(pattern_percentage_float) > 0:
        segmented_text_list = list(map(
            lambda x: percentage_float_key_num_pairs[x] if x in percentage_float_key_num_pairs.keys() else x, segmented_text_list))
    if len(pattern_percentage_int) > 0:
        segmented_text_list = list(map(
            lambda x: percentage_int_key_num_pairs[x] if x in percentage_int_key_num_pairs.keys() else x, segmented_text_list))
    if len(pattern_float) > 0:
        segmented_text_list = list(map(
            lambda x: float_key_num_pairs[x] if x in float_key_num_pairs.keys() else x, segmented_text_list))
    if len(pattern_int) > 0:
        segmented_text_list = list(map(
            lambda x: int_key_num_pairs[x] if x in int_key_num_pairs.keys() else x, segmented_text_list))

    return segmented_text_list


def generate_group_num(syntactic_dependencies_list, num_list, process_lv=2):

    # hanlp依存句法分析结果中，该问题各个num_list成员的索引
    num_list_index = list(
        filter(lambda x: x[1] in num_list, syntactic_dependencies_list))
    num_list_index = list(map(lambda x: x[0], num_list_index))

    # 初始化每个quality cell成员内容列表
    group_num_segs = []
    # 初始化每个quality cell成员索引列表
    group_num = []

    if process_lv == 1:
        # 一层
        # 对于group_num中的每个num，左（修饰/依赖该num的）右（被该num修饰/依赖）各找一个分词（遇到标点舍弃），如果不足一个，则补满一个，补充方法就是简单地往左/往右摘取（遇到标点舍弃）
        for num_index in num_list_index:

            num_index_real = int(num_index)-1
            num_list_member = syntactic_dependencies_list[num_index_real]
            num = num_list_member[1]

            left_index = list(
                filter(lambda x: (x[6] == num_index) and (x[1] not in cn_en_punctuations_set), syntactic_dependencies_list))
            left_index = list(map(lambda x: x[0], left_index))
            left_index.sort(key=lambda x: int(x))

            right_index = list(
                filter(lambda x: (x[0] == num_list_member[6]) and (x[1] not in cn_en_punctuations_set), syntactic_dependencies_list))
            right_index = list(map(lambda x: x[0], right_index))
            right_index.sort(key=lambda x: int(x))

            combined_indices = left_index + [num_index] + right_index
            combined_indices.sort(key=lambda x: int(x))

            left_index_adjusted = []
            right_index_adjusted = []
            for j, i in enumerate(combined_indices):
                if i != num_index:
                    left_index_adjusted.append(i)
                else:
                    break

            for k, i in enumerate(combined_indices):
                if k <= j:
                    continue
                else:
                    right_index_adjusted.append(i)

            if len(left_index_adjusted) == 0:
                left_index_adjusted_min = int(num_index)
                if (1 <= left_index_adjusted_min-1 <= len(syntactic_dependencies_list)) and (syntactic_dependencies_list[left_index_adjusted_min-2][1] not in cn_en_punctuations_set):
                    left_index_adjusted.append(
                        f'{left_index_adjusted_min-1}')
                    left_index_adjusted.sort(
                        key=lambda x: int(x))

            if len(right_index_adjusted) == 0:
                right_index_adjusted_max = int(num_index)
                if (1 <= right_index_adjusted_max+1 <= len(syntactic_dependencies_list)) and (syntactic_dependencies_list[right_index_adjusted_max][1] not in cn_en_punctuations_set):
                    right_index_adjusted.append(
                        f'{right_index_adjusted_max+1}')
                    right_index_adjusted.sort(
                        key=lambda x: int(x))

            combined_indices_ext = left_index_adjusted + \
                [num_index] + right_index_adjusted

            combined = [syntactic_dependencies_list[int(i)-1][1]
                        for i in combined_indices_ext]
            combined_i = [int(i)-1 for i in combined_indices_ext]

            group_num_segs.append(combined)
            group_num.extend(combined_i)

    elif process_lv == 2:
        # 二层
        # 对于group_num中的每个num，左（修饰/依赖该num的）右（被该num修饰/依赖）各找两个分词（遇到标点舍弃），如果不足两个，则补满两个，补充方法就是简单地往左/往右摘取（遇到标点舍弃）
        for num_index in num_list_index:

            num_index_real = int(num_index)-1
            num_list_member = syntactic_dependencies_list[num_index_real]
            num = num_list_member[1]

            left_index = list(
                filter(lambda x: (x[6] == num_index) and (x[1] not in cn_en_punctuations_set), syntactic_dependencies_list))
            left_index = list(map(lambda x: x[0], left_index))
            left_index.sort(key=lambda x: int(x))
            left_segs_lv_1 = [syntactic_dependencies_list[int(i)-1][1]
                              for i in left_index if (0 <= int(i)-1 < len(syntactic_dependencies_list))]

            # print(
            #     f'for num: {num}, num_index: {num_index}, left_segs_lv_1: {left_segs_lv_1}')

            left_segs_indices = []
            for num_index_left in left_index:

                num_left_seg = syntactic_dependencies_list[int(
                    num_index_left)-1][1]

                left_index_left = list(
                    filter(lambda x: (x[6] == num_index_left) and (x[1] not in cn_en_punctuations_set), syntactic_dependencies_list))
                left_index_left = list(
                    map(lambda x: x[0], left_index_left))
                left_index_left.sort(key=lambda x: int(x))

                left_index_right = list(
                    filter(lambda x: (x[0] == syntactic_dependencies_list[int(num_index_left)-1][6]) and (x[0] not in num_list_index) and (x[1] not in cn_en_punctuations_set), syntactic_dependencies_list))
                left_index_right = list(
                    map(lambda x: x[0], left_index_right))
                left_index_right.sort(key=lambda x: int(x))

                left_segs_indices += (left_index_left +
                                      [num_index_left] + left_index_right)

                # print(
                #     f'for num: {num}, num_index: {num_index}, num_left_seg: {num_left_seg}, left_segs_indices: {left_segs_indices}')

            # print(
            #     f'for num: {num}, num_index: {num_index}, left_segs_indices: {left_segs_indices}')

            right_index = list(
                filter(lambda x: (x[0] == num_list_member[6]) and (x[1] not in cn_en_punctuations_set), syntactic_dependencies_list))
            right_index = list(map(lambda x: x[0], right_index))
            right_index.sort(key=lambda x: int(x))
            right_segs_lv_1 = [syntactic_dependencies_list[int(i)-1][1]
                               for i in right_index if (0 <= int(i)-1 < len(syntactic_dependencies_list))]

            # print(
            #     f'for num: {num}, num_index: {num_index}, right_segs_lv_1: {right_segs_lv_1}')

            right_segs_indices = []
            for num_index_right in right_index:

                num_right_seg = syntactic_dependencies_list[int(
                    num_index_right)-1][1]

                right_index_left = list(
                    filter(lambda x: (x[6] == num_index_right) and (x[0] not in num_list_index) and (x[1] not in cn_en_punctuations_set), syntactic_dependencies_list))
                right_index_left = list(
                    map(lambda x: x[0], right_index_left))
                right_index_left.sort(key=lambda x: int(x))

                right_index_right = list(
                    filter(lambda x: (x[0] == syntactic_dependencies_list[int(num_index_right)-1][6]) and (x[1] not in cn_en_punctuations_set), syntactic_dependencies_list))
                right_index_right = list(
                    map(lambda x: x[0], right_index_right))
                right_index_right.sort(key=lambda x: int(x))

                right_segs_indices += (right_index_left +
                                       [num_index_right] + right_index_right)

                # print(
                #     f'for num: {num}, num_index: {num_index}, num_right_seg: {num_right_seg}, right_segs_indices: {right_segs_indices}')

            # print(
            #     f'for num: {num}, num_index: {num_index}, right_segs_indices: {right_segs_indices}')

            combined_indices = left_segs_indices + \
                [num_index] + right_segs_indices
            combined_indices.sort(key=lambda x: int(x))

            left_segs_indices_adjusted = []
            right_segs_indices_adjusted = []
            for j, i in enumerate(combined_indices):
                if i != num_index:
                    left_segs_indices_adjusted.append(i)
                else:
                    break

            for k, i in enumerate(combined_indices):
                if k <= j:
                    continue
                else:
                    right_segs_indices_adjusted.append(i)

            if len(left_segs_indices_adjusted) == 1:
                left_segs_indices_adjusted_min = int(
                    left_segs_indices_adjusted[0])
                if (1 <= left_segs_indices_adjusted_min-1 <= len(syntactic_dependencies_list)) and (syntactic_dependencies_list[left_segs_indices_adjusted_min-2][1] not in cn_en_punctuations_set):
                    left_segs_indices_adjusted.append(
                        f'{left_segs_indices_adjusted_min-1}')
                    left_segs_indices_adjusted.sort(
                        key=lambda x: int(x))
            elif len(left_segs_indices_adjusted) == 0:
                left_segs_indices_adjusted_min = int(num_index)
                if (1 <= left_segs_indices_adjusted_min-1 <= len(syntactic_dependencies_list)) and (syntactic_dependencies_list[left_segs_indices_adjusted_min-2][1] not in cn_en_punctuations_set):
                    left_segs_indices_adjusted.append(
                        f'{left_segs_indices_adjusted_min-1}')
                if (1 <= left_segs_indices_adjusted_min-2 <= len(syntactic_dependencies_list)) and (syntactic_dependencies_list[left_segs_indices_adjusted_min-3][1] not in cn_en_punctuations_set):
                    left_segs_indices_adjusted.append(
                        f'{left_segs_indices_adjusted_min-2}')
                left_segs_indices_adjusted.sort(
                    key=lambda x: int(x))

            if len(right_segs_indices_adjusted) == 1:
                right_segs_indices_adjusted_max = int(
                    right_segs_indices_adjusted[0])
                if (1 <= right_segs_indices_adjusted_max+1 <= len(syntactic_dependencies_list)) and (syntactic_dependencies_list[right_segs_indices_adjusted_max][1] not in cn_en_punctuations_set):
                    right_segs_indices_adjusted.append(
                        f'{right_segs_indices_adjusted_max+1}')
                    right_segs_indices_adjusted.sort(
                        key=lambda x: int(x))
            elif len(right_segs_indices_adjusted) == 0:
                right_segs_indices_adjusted_max = int(num_index)
                if (1 <= right_segs_indices_adjusted_max+1 <= len(syntactic_dependencies_list)) and (syntactic_dependencies_list[right_segs_indices_adjusted_max][1] not in cn_en_punctuations_set):
                    right_segs_indices_adjusted.append(
                        f'{right_segs_indices_adjusted_max+1}')
                if (1 <= right_segs_indices_adjusted_max+2 <= len(syntactic_dependencies_list)) and (syntactic_dependencies_list[right_segs_indices_adjusted_max+1][1] not in cn_en_punctuations_set):
                    right_segs_indices_adjusted.append(
                        f'{right_segs_indices_adjusted_max+2}')
                right_segs_indices_adjusted.sort(
                    key=lambda x: int(x))

            combined_indices_ext = left_segs_indices_adjusted + \
                [num_index] + right_segs_indices_adjusted

            combined = [syntactic_dependencies_list[int(i)-1][1]
                        for i in combined_indices_ext]
            combined_i = [int(i)-1 for i in combined_indices_ext]

            group_num_segs.append(combined)
            group_num.extend(combined_i)

    return group_num, group_num_segs


# 最长公共子串 (The Longest Common Substring)
def find_lcsubstr(s1, s2):
    m = [[0 for i in range(len(s2)+1)]
         for j in range(len(s1)+1)]  # 生成0矩阵，为方便后续计算，比字符串长度多了一列
    mmax = 0  # 最长匹配的长度
    p = 0  # 最长匹配对应在s1中的最后一位
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                m[i+1][j+1] = m[i][j]+1
                if m[i+1][j+1] > mmax:
                    mmax = m[i+1][j+1]
                    p = i+1
    return s1[p-mmax:p], mmax  # 返回最长子串及其长度


# print find_lcsubstr('abcdfg', 'abdfg')


def del_add_info(str_):

    question_with_spaces_deleted = str_

    # 在查看问题中的关键词时，某些判断还要把额外信息去掉，所以再准备一个变量 question_without_add_info
    # 以英文括号结尾，某些结尾可能是【).】【)?】 等等，所以倒数第2个字符是也算
    if question_with_spaces_deleted.endswith(')') or (question_with_spaces_deleted[-2] == ')'):
        reversed_ = question_with_spaces_deleted[::-1]
        try:
            index_ = reversed_.index('(')
        except:
            try:
                index_ = reversed_.index('（')
            except:
                index_ = -1
        if index_ > 0:
            question_without_add_info = question_with_spaces_deleted[:(
                0-index_-1)]
        else:
            question_without_add_info = question_with_spaces_deleted

    # 以中文括号结尾，某些结尾可能是【）。】【）？】 等等，所以倒数第2个字符是也算
    elif question_with_spaces_deleted.endswith('）') or (question_with_spaces_deleted[-2] == '）'):
        reversed_ = question_with_spaces_deleted[::-1]
        try:
            index_ = reversed_.index('（')
        except:
            try:
                index_ = reversed_.index('(')
            except:
                index_ = -1
        if index_ > 0:
            question_without_add_info = question_with_spaces_deleted[:(
                0-index_-1)]
        else:
            question_without_add_info = question_with_spaces_deleted

    else:
        question_without_add_info = question_with_spaces_deleted

    return question_without_add_info


units_mention_re = r'多少[平方|立方|米|分米|厘米|千米|毫米|公顷|克|毫克|千克|吨|方|毫升|升|小时|分钟|秒钟|摄氏度|华氏度|度]'
units_mention_re2 = r'几[平方|立方|米|分米|厘米|千米|毫米|公顷|克|毫克|千克|吨|方|毫升|升|小时|分钟|秒钟|摄氏度|华氏度|度]'


def generate_ans_and_post_process_for_competition_format(question_cleaned, equation_infix_for_eval_ans, doc_index_to_inspect=-1):
    global units_mention_re
    global units_mention_re2
    if equation_infix_for_eval_ans.startswith('x='):
        equation_infix_for_eval_ans = equation_infix_for_eval_ans[2:]

    equation_for_eval_ans = equation_infix_for_eval_ans

    # 小数百分数匹配列表
    pattern_percentage_float = re.findall(
        r'(\d+\.\d+%)', equation_for_eval_ans)
    if len(pattern_percentage_float) > 0:
        # print(i, equation_for_eval_ans)
        pattern_percentage_float.sort(
            key=lambda x: len(x), reverse=True)

        for percentage_float in pattern_percentage_float:
            equation_for_eval_ans = equation_for_eval_ans.replace(
                percentage_float, f'({percentage_float[:-1]}/100)')

        # print(i, equation_for_eval_ans)

    # 整数百分数匹配列表
    pattern_percentage_int = re.findall(r'(\d+%)', equation_for_eval_ans)
    if len(pattern_percentage_int) > 0:
        # print(i, equation_for_eval_ans)

        pattern_percentage_int.sort(
            key=lambda x: len(x), reverse=True)

        for percentage_int in pattern_percentage_int:
            equation_for_eval_ans = equation_for_eval_ans.replace(
                percentage_int, f'({percentage_int[:-1]}/100)')
        # print(i, equation_for_eval_ans)

    equation_for_eval_ans = equation_for_eval_ans.replace('^', '**')

    if doc_index_to_inspect > 0:
        print(
            f'for doc_index: {doc_index_to_inspect}, equation_for_eval_ans processed is: {equation_for_eval_ans}\n')

    question_with_spaces_deleted = question_cleaned

    question_without_add_info = del_add_info(question_with_spaces_deleted)

    # 最后20个字符（包括额外信息）
    last_20_chars = question_with_spaces_deleted[-20:]
    # 最后20个字符（不包括额外信息）
    last_20_chars_without_add_info = question_without_add_info[-20:]

    # 某些判断需按分隔类标点标点断句，这里以去除额外信息的问句为基础
    # 可以比较下是从最后n个字符中找关键词更好，还是从最后一个，或者倒数第二个子句中找关键词更好

    question_sep_by_seg_punctuations = sep_by_seg_punctuations(
        question_without_add_info)

    if doc_index_to_inspect > 0:
        print(
            f'for doc_index: {doc_index_to_inspect}, question_with_spaces_deleted is: {question_with_spaces_deleted}')
        print(
            f'for doc_index: {doc_index_to_inspect}, last_20_chars is: {last_20_chars}')
        print(
            f'for doc_index: {doc_index_to_inspect}, last_20_chars_without_add_info is: {last_20_chars_without_add_info}')
        print(
            f'for doc_index: {doc_index_to_inspect}, question_sep_by_seg_punctuations is: {question_sep_by_seg_punctuations}\n')

    # 条件：最后一个子句（不包括额外信息）含有“百分”的
    cond_percentage_in_last_sep = len(question_sep_by_seg_punctuations) >= 1 \
        and ('百分' in question_sep_by_seg_punctuations[-1])

    if doc_index_to_inspect > 0:
        print(
            f'for doc_index: {doc_index_to_inspect}, cond_percentage_in_last_sep is: {cond_percentage_in_last_sep}\n')

    # TODO doc_index train 89 率的问题，仍然没有化为百分数
    # 条件：最后一个子句（不包括额外信息）含有“率”的，其他增加条件说明详见data_process_post.py
    cond_rate_in_last_sep = len(question_sep_by_seg_punctuations) >= 1 \
        and ('率' in question_sep_by_seg_punctuations[-1]) \
        and ('%' not in question_sep_by_seg_punctuations[-1]) \
        and ('率的' not in question_sep_by_seg_punctuations[-1])

    if doc_index_to_inspect > 0:
        print(
            f'for doc_index: {doc_index_to_inspect}, cond_rate_in_last_sep is: {cond_rate_in_last_sep}\n')

    # 首先构造比率类关键词+问句标志词列表
    rate_keywords = ['浓度', '纯度', '盐度', '咸度', '饱和度']
    combination1_rate = [f'{item}是多少' for item in rate_keywords]
    combination2_rate = [f'{item}为多少' for item in rate_keywords]
    combination3_rate = [f'{item}多少' for item in rate_keywords]
    combination4_rate = [f'{item}？' for item in rate_keywords]
    combination5_rate = [f'{item}?' for item in rate_keywords]

    combination_rate = \
        combination1_rate + \
        combination2_rate + \
        combination3_rate + \
        combination4_rate + \
        combination5_rate

    # 条件：最后一个子句（不包括额外信息）中含有比率类关键词的
    with_rate_keywords_in_last_sep = False
    for rate_keyword in combination_rate:
        if rate_keyword in question_sep_by_seg_punctuations[-1]:
            with_rate_keywords_in_last_sep = True
            break

    # 条件：最后一个子句（不包括额外信息）中含有“几分之”的
    cond_fraction_in_last_sep = '几分之' in question_sep_by_seg_punctuations[-1]

    if doc_index_to_inspect > 0:
        print(
            f'for doc_index: {doc_index_to_inspect}, cond_fraction_in_last_sep is: {cond_fraction_in_last_sep}\n')

    # 首先构造比例类关键词+问句标志词列表
    ratio_keywords = ['比例', '比率', '比重', '占比']
    combination1_ratio = [f'{item}是多少' for item in ratio_keywords]
    combination2_ratio = [f'{item}为多少' for item in ratio_keywords]
    combination3_ratio = [f'{item}多少' for item in ratio_keywords]
    combination4_ratio = [f'{item}？' for item in ratio_keywords]
    combination5_ratio = [f'{item}?' for item in ratio_keywords]

    combination_ratio = \
        combination1_ratio + \
        combination2_ratio + \
        combination3_ratio + \
        combination4_ratio + \
        combination5_ratio

    # 条件：最后一个子句（不包括额外信息）中含有比例类关键词的
    with_ratio_keywords_in_last_sep = False
    for ratio_keyword in combination_ratio:
        if ratio_keyword in question_sep_by_seg_punctuations[-1]:
            with_ratio_keywords_in_last_sep = True
            break

    if doc_index_to_inspect > 0:
        print(
            f'for doc_index: {doc_index_to_inspect}, with_ratio_keywords_in_last_sep is: {with_ratio_keywords_in_last_sep}\n')

    try:
        eval_result_py = eval(equation_for_eval_ans)
        # eval_result_py = eval_str(equation_for_eval_ans)
    except:
        eval_result_py = ''
        ans = ''
        equation_for_eval_ans = ''

    # 注意：如果用eval()处理eval_result_py，eval_result_py一定要是str，且不为空
    # 注意：如果用round_up()或是ceil()或是floor()处理eval_result_py，eval_result_py一定要是数字类型，而不是str
    if isinstance(eval_result_py, str) and (eval_result_py != ''):
        eval_result_py = eval(eval_result_py)

    if equation_for_eval_ans != '':
        expr_infix = equation_for_eval_ans
    else:
        expr_infix = ''

    if expr_infix != '':

        if doc_index_to_inspect > 0:
            print(
                f'for doc_index: {doc_index_to_inspect}, expr_infix is here: {expr_infix}\n')

        if (re.findall(r'多少[辆|人|个|只|箱|本|次|张|块|条]', question_sep_by_seg_punctuations[-1]) or
                re.findall(r'几[辆|人|个|只|箱|包|本|次|张|块|条]', question_sep_by_seg_punctuations[-1])):

            if re.findall(r'至少|最少|起码|租|船|拉完|运完|需要|需|要|限乘|乘坐|准乘|限载|限坐', question_sep_by_seg_punctuations[-1]) or (len(question_sep_by_seg_punctuations) > 1 and re.findall(r'只能|限乘|乘坐|准乘|限载|限坐', question_sep_by_seg_punctuations[-2])):
                ans = ceil(eval_result_py)
            elif re.findall(r'至多|最多|顶多|可以|分|能|一共', question_sep_by_seg_punctuations[-1]):
                ans = floor(eval_result_py)
            else:
                ans = int(eval_result_py+0.5)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #1! And the ans is: {ans}\n')

        elif (re.findall(r'多少[圈|顶|桶]', question_sep_by_seg_punctuations[-1]) or re.findall(r'几[圈|顶|桶]', question_sep_by_seg_punctuations[-1])):

            if re.findall(r'至少|最少|起码|需要', question_sep_by_seg_punctuations[-1]):
                ans = ceil(eval_result_py)
            else:
                ans = int(eval_result_py+0.5)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #2! And the ans is: {ans}\n')

        elif re.findall(r'多少[束|件|副|头|幅|排|枝|枝|根|瓶|盒|组|袋|套]', question_sep_by_seg_punctuations[-1]) or re.findall(r'几[束|件|副|头|幅|排|枝|枝|根|瓶|盒|组|袋|套]', question_sep_by_seg_punctuations[-1]):

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #3!\n')

            if re.findall(r'至多|最多|顶多|可以|能|可', question_sep_by_seg_punctuations[-1]):

                if doc_index_to_inspect > 0:
                    print(
                        f'for doc_index: {doc_index_to_inspect}, we are in cond #3 @@!\n')

                ans = floor(eval_result_py)
            else:

                if doc_index_to_inspect > 0:
                    print(
                        f'for doc_index: {doc_index_to_inspect}, we are in cond #3 @@@@!\n')

                ans = int(eval_result_py+0.5)

                if doc_index_to_inspect > 0:
                    print(
                        f'for doc_index: {doc_index_to_inspect}, we are in cond #3 @@@@@@!\n')

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #3! And the ans is: {ans}\n')

        elif re.findall(r'至少|最少|起码', question_sep_by_seg_punctuations[-1]) or (len(question_sep_by_seg_punctuations) > 1 and re.findall(r'至少|最少', question_sep_by_seg_punctuations[-2])):

            if (re.findall(units_mention_re, question_sep_by_seg_punctuations[-1]) or re.findall(units_mention_re2, question_sep_by_seg_punctuations[-1])):
                if '保留整' in last_20_chars:
                    ans = ceil(eval_result_py)
                else:
                    is_there_float_in_expr_infix = False
                    for item in expr_infix:
                        if '.' in f'{item}':
                            is_there_float_in_expr_infix = True
                            break
                    if is_there_float_in_expr_infix:
                        ans = round_up(
                            eval_result_py, keep_float_bits=5)
                        if f'{ans}'.endswith('.0'):
                            ans = f'{ans}'[:-2]
                    else:
                        # ans = simplify(expr_infix)
                        ans = eval(
                            re.sub(r'([\d]+)', 'Integer(\\1)', expr_infix))
                        if '.' in f'{ans}':
                            ans = round_up(eval(f'{ans}'), keep_float_bits=5)
                        if f'{ans}'.endswith('.0'):
                            ans = f'{ans}'[:-2]
            else:
                ans = ceil(eval_result_py)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #4! And the ans is: {ans}\n')

        elif re.findall(r'至多|最多|顶多', question_sep_by_seg_punctuations[-1]):

            if (re.findall(units_mention_re, question_sep_by_seg_punctuations[-1]) or re.findall(units_mention_re2, question_sep_by_seg_punctuations[-1])):
                if '保留整' in last_20_chars:
                    ans = floor(eval_result_py)
                else:
                    is_there_float_in_expr_infix = False
                    for item in expr_infix:
                        if '.' in f'{item}':
                            is_there_float_in_expr_infix = True
                            break
                    if is_there_float_in_expr_infix:
                        ans = round_up(
                            eval_result_py, keep_float_bits=5)
                        if f'{ans}'.endswith('.0'):
                            ans = f'{ans}'[:-2]
                    else:
                        # ans = simplify(expr_infix)
                        ans = eval(
                            re.sub(r'([\d]+)', 'Integer(\\1)', expr_infix))
                        if '.' in f'{ans}':
                            ans = round_up(eval(f'{ans}'), keep_float_bits=5)
                        if f'{ans}'.endswith('.0'):
                            ans = f'{ans}'[:-2]
            else:
                ans = floor(eval_result_py)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #5! And the ans is: {ans}\n')

        elif (len(question_sep_by_seg_punctuations) > 1) and re.findall(r'至多|最多|顶多', question_sep_by_seg_punctuations[-2]) and ('多少' not in question_sep_by_seg_punctuations[-2]):

            if (re.findall(units_mention_re, question_sep_by_seg_punctuations[-1]) or re.findall(units_mention_re2, question_sep_by_seg_punctuations[-1])):
                if '保留整' in last_20_chars:
                    ans = floor(eval_result_py)
                else:
                    ans = ceil(eval_result_py)
            else:
                ans = ceil(eval_result_py)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #6! And the ans is: {ans}\n')

        elif cond_percentage_in_last_sep or cond_rate_in_last_sep or with_rate_keywords_in_last_sep:

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #7!\n')

            if ('保留整数' in last_20_chars) or \
                ('保留到1%' in last_20_chars) or \
                ('保留到百分之一' in last_20_chars) or \
                ('精确到1%' in last_20_chars) or \
                    ('精确到百分之一' in last_20_chars):
                percentage_num = int(eval_result_py * 100 + 0.5)
            elif ('保留一位' in last_20_chars) or \
                ('保留1位' in last_20_chars) or \
                ('保留到0.1%' in last_20_chars) or \
                    ('精确到0.1%' in last_20_chars):
                percentage_num = round_up(
                    eval_result_py * 100, keep_float_bits=1)
            elif ('保留二位' in last_20_chars) or \
                ('保留两位' in last_20_chars) or \
                ('保留2位' in last_20_chars) or \
                ('保留到0.01%' in last_20_chars) or \
                    ('精确到0.01%' in last_20_chars):
                percentage_num = round_up(
                    eval_result_py * 100, keep_float_bits=2)
                float_num_bits = f'{percentage_num}'.split('.')[1]
                if len(float_num_bits) < 2:
                    percentage_num = f'{percentage_num}0'
            else:
                # 现改为百分号前的小数默认保留一位
                percentage_num = round_up(
                    eval_result_py * 100, keep_float_bits=1)
                if f'{percentage_num}'.endswith('.0'):
                    percentage_num = f'{percentage_num}'[:-2]
            ans = f'{percentage_num}%'

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #7! And the ans is: {ans}\n')

        elif cond_fraction_in_last_sep or with_ratio_keywords_in_last_sep:

            # 小数匹配列表
            pattern_float = re.findall(r'(\d+\.\d+)', expr_infix)

            if len(pattern_float) > 0:
                pattern_float.sort(key=lambda x: len(x), reverse=True)
                for _i, float_ in enumerate(pattern_float):
                    expr_infix = expr_infix.replace(
                        float_, str(Fraction(eval(f'{float_}')).limit_denominator()))

            # ans = simplify(expr_infix)
            ans = eval(
                re.sub(r'([\d]+)', 'Integer(\\1)', expr_infix))
            if '.' in f'{ans}':
                ans = round_up(eval(f'{ans}'), keep_float_bits=5)
            if f'{ans}'.endswith('.0'):
                ans = f'{ans}'[:-2]

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #8! And the ans is: {ans}\n')

        elif ('保留到个位' in last_20_chars) or \
            ('保留个位' in last_20_chars) or \
            ('精确到个位' in last_20_chars) or \
            ('保留整' in last_20_chars) or \
            ('精确到整' in last_20_chars) or \
            ('保留到1' in last_20_chars) or \
                ('精确到1' in last_20_chars):
            ans = int(eval_result_py+0.5)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #9! And the ans is: {ans}\n')

        elif ('保留一位' in last_20_chars) or \
            ('保留1位' in last_20_chars) or \
            ('保留0.1' in last_20_chars) or \
            ('保留到0.1' in last_20_chars) or \
            ('精确到0.1' in last_20_chars) or \
            ('保留到十分位' in last_20_chars) or \
            ('保留十分位' in last_20_chars) or \
            ('精确到十分位' in last_20_chars) or \
            ('保留到小数点后一位' in last_20_chars) or \
            ('保留到小数点后1位' in last_20_chars) or \
            ('保留小数点后一位' in last_20_chars) or \
            ('保留小数点后1位' in last_20_chars) or \
            ('精确到小数点后一位' in last_20_chars) or \
                ('精确到小数点后1位' in last_20_chars):
            ans = round_up(eval_result_py, keep_float_bits=1)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #10! And the ans is: {ans}\n')
        elif ('保留两位' in last_20_chars) or \
            ('保留二位' in last_20_chars) or \
            ('保留2位' in last_20_chars) or \
            ('保留0.01' in last_20_chars) or \
            ('保留到0.01' in last_20_chars) or \
            ('精确到0.01' in last_20_chars) or \
            ('保留到百分位' in last_20_chars) or \
            ('保留百分位' in last_20_chars) or \
            ('精确到百分位' in last_20_chars) or \
            ('保留到小数点后两位' in last_20_chars) or \
            ('保留到小数点后二位' in last_20_chars) or \
            ('保留到小数点后2位' in last_20_chars) or \
            ('保留小数点后两位' in last_20_chars) or \
            ('保留小数点后二位' in last_20_chars) or \
            ('保留小数点后2位' in last_20_chars) or \
            ('精确到小数点后两位' in last_20_chars) or \
            ('精确到小数点后二位' in last_20_chars) or \
                ('精确到小数点后2位' in last_20_chars):
            ans = round_up(eval_result_py, keep_float_bits=2)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #11! And the ans is: {ans}\n')

        elif ('保留三位' in last_20_chars) or \
            ('保留3位' in last_20_chars) or \
            ('保留0.001' in last_20_chars) or \
            ('保留到0.001' in last_20_chars) or \
            ('精确到0.001' in last_20_chars) or \
            ('保留到千分位' in last_20_chars) or \
            ('保留千分位' in last_20_chars) or \
            ('精确到千分位' in last_20_chars) or \
            ('保留到小数点后三位' in last_20_chars) or \
            ('保留到小数点后3位' in last_20_chars) or \
            ('保留小数点后三位' in last_20_chars) or \
            ('保留小数点后3位' in last_20_chars) or \
            ('精确到小数点后三位' in last_20_chars) or \
                ('精确到小数点后3位' in last_20_chars):
            ans = round_up(eval_result_py, keep_float_bits=3)

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #12! And the ans is: {ans}\n')

        # 比例尺类问题保留小数
        elif '比例尺' in question_with_spaces_deleted:
            ans = eval_result_py
            if '.' in f'{ans}':
                ans = round_up(eval(f'{ans}'), keep_float_bits=5)
            if f'{ans}'.endswith('.0'):
                ans = f'{ans}'[:-2]

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #13! And the ans is: {ans}\n')

        else:
            # print('here!')
            is_there_float_in_expr_infix = False
            for item in expr_infix:
                if '.' in f'{item}':
                    is_there_float_in_expr_infix = True
                    break
            # TODO doc_index 108 保留了3位！！
            if is_there_float_in_expr_infix:
                ans = round_up(eval_result_py, keep_float_bits=5)
                if f'{ans}'.endswith('.0'):
                    ans = f'{ans}'[:-2]
            else:
                # ans = simplify(expr_infix)
                ans = eval(
                    re.sub(r'([\d]+)', 'Integer(\\1)', expr_infix))
                if '.' in f'{ans}':
                    ans = round_up(eval(f'{ans}'), keep_float_bits=5)
                if f'{ans}'.endswith('.0'):
                    ans = f'{ans}'[:-2]

            if doc_index_to_inspect > 0:
                print(
                    f'for doc_index: {doc_index_to_inspect}, we are in cond #14! And the ans is: {ans}\n')

    # 转为字符串
    ans = f'{ans}'

    return ans


if __name__ == '__main__':

    expr1 = "3000/(3000/5+150)"
    expr2 = "3.14*2^2*2+2*3.14*2*10"
    expr3 = "2*(1-(1/4))"
    expr4 = "3.14*2^2*2*3*4+2*3.14*2*10"
    expr5 = "11/7"

    expr1_sympy_simplified = simplify(expr1)
    print('expr1_sympy_simplified:')
    pprint.pprint(expr1_sympy_simplified)
    print()

    expr3_sympy_simplified = simplify(expr3)
    print('expr3_sympy_simplified:')
    pprint.pprint(expr3_sympy_simplified)
    print()

    expr4_sympy_simplified = simplify(expr4)
    print('expr4_sympy_simplified:')
    pprint.pprint(expr4_sympy_simplified)
    print()

    expr5_sympy_simplified = simplify(expr5)
    print('expr4_sympy_simplified:')
    pprint.pprint(expr5_sympy_simplified)
    print()

    expr1 = ['3000', '/', '(', '3000', '/', '5', '+', '150', ')']
    expr2 = ['3.14', '*', '2', '^', '2', '*', '2',
             '+', '2', '*', '3.14', '*', '2', '*', '10']
    expr3 = ['2', '*', '(', '1', '-', '(', '1', '/', '4', ')', ')']
    expr4 = ['3.14', '*', '2', '^', '2', '*', '2', '*', '3', '*', '4',
             '+', '2', '*', '3.14', '*', '2', '*', '10']

    expr1_prefix = from_infix_to_prefix(expr1)
    expr2_prefix = from_infix_to_prefix(expr2)
    expr3_prefix = from_infix_to_prefix(expr3)
    expr4_prefix = from_infix_to_prefix(expr4)

    print('expr1_prefix:')
    pprint.pprint(expr1_prefix)
    print()

    print('expr2_prefix:')
    pprint.pprint(expr2_prefix)
    print()

    print('expr3_prefix:')
    pprint.pprint(expr3_prefix)
    print()

    print('expr4_prefix:')
    pprint.pprint(expr4_prefix)
    print()

    print('parse_and_eval_prefix_expr():')
    print(parse_and_eval_prefix_expr(expr1_prefix))
    print(parse_and_eval_prefix_expr(expr2_prefix))
    print(parse_and_eval_prefix_expr(expr3_prefix))
    print(parse_and_eval_prefix_expr(expr4_prefix))
    print()

    print('compute_prefix_expression():')
    print(compute_prefix_expression(expr1_prefix))
    print()

    q_str = '有一个直径是16m的圆形花坛，沿着它的四周修一条宽1m的小路，这条小路的面积是多少平方米？'
    print('del_cn_en_punctuations():')
    print(del_cn_en_punctuations(q_str))
    print()
