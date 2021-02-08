import copy
import json
import operator
import pprint
import re
import traceback
from collections import OrderedDict, deque
from copy import deepcopy
from fractions import Fraction
from math import ceil, floor
from string import ascii_letters, digits, punctuation

from sympy import Integer, simplify
from tqdm import tqdm

cn_punctuations = '：、「」，。！？【】（）％＃＠＆“”‘’–—−‑——'
cn_punctuations2 = """！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘'‛“”„‟…‧﹏."""
cn_seg_punctuations = '！？｡。，､、〟；'

cn_en_punctuations_set = set(cn_punctuations).union(
    set(cn_punctuations2)).union(set(cn_seg_punctuations)).union(set(punctuation))

# 小数点不算seg_punctuation，英文句号以．表示 wrong
# 用来断句的，不仅以点为判断依据，还要看点后面是不是数字
# 英文分隔类标点（去除两种点．.，单独判断小数点）
en_seg_punctuations = '!?,;'
# 中英文分隔类标点集合
cn_en_seg_punctuations_set = set(
    cn_seg_punctuations).union(set(en_seg_punctuations))

# 将英文标点转为中文标点
# https://blog.csdn.net/qq_26870933/article/details/83059551
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
    '【': '(',
    '】': ')',
    '「': '(',
    '」': ')',
    '[': '(',
    ']': ')',
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

# 表示比例的中文冒号转为英文冒号
def convert_cn_colon_to_en(str_):
    str_list = list(str_)
    for i, char in enumerate(str_list):
        if (i > 0) and (i < len(str_list) - 1) and (char == '：') and \
            ((str_list[i-1] in digits) or (str_list[i-1] == '?') or (str_list[i-1] == '？') or (str_list[i-1] == '少') or (str_list[i-1] == '几')) and \
                ((str_list[i+1] in digits) or (str_list[i+1] == '?') or (str_list[i+1] == '？') or (str_list[i+1] == '多') or (str_list[i+1] == '几')):
            str_list[i] = ':'
    return ''.join(str_list)

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
    # 删除空格，`，unicode字符
    for char in str_:
        if (char == ' ') or (char == '`') or (char in unicode_to_rm) or (char.strip() == ''):
            pass
        else:
            str_ret += char

    # 去除html中的标记：
    str_ret = str_ret.replace('&thinsp;', '')
    str_ret = str_ret.replace('&nbsp;', '')
    str_ret = str_ret.replace('&nbip;', '')
    str_ret = str_ret.replace('&ensp;', '')
    str_ret = str_ret.replace('&emsp;', '')
    str_ret = str_ret.replace('&zwnj;', '')
    str_ret = str_ret.replace('&zwj;', '')
    return str_ret.strip()

# 过滤标点符号
def filter_all_is_punctuation(str_):
    all_is_punctuation = True
    for char in str_:
        if char not in cn_en_punctuations_set:
            all_is_punctuation = False
            break
    return all_is_punctuation

# 按标点拆分句子
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

def replace_underscore_with_how_much(str_):
    for i in range(20, 1, -1):
        str_ = str_.replace('_' * i, '多少')
    return str_

# 超过1个字符的表述替换
def convert_some_mentions(str_):
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
    # https://www.jb51.net/article/159505.htm
    # 替换内置round函数,实现默认保留2位小数的精确四舍五入
    return round(value * 10**keep_float_bits) / float(10**keep_float_bits)

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
units_mention_unified['r'] = '半径'

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

# 对待转换的关键词，根据其长度进行排序，越长越靠前，因为越长则特指性越强，应优先替换
# 如：cm应替换成“厘米”，而不是将其中的m替换成“米”
keys = sorted(units_mention_unified.keys(),
              key=lambda x: len(x), reverse=True)

# 初始化一个有序字典
units_mention_unified_ordered = OrderedDict()
# 依据上面排好序的key，重新构造一个有序字典，用于问题中的单位转换
for key in keys:
    units_mention_unified_ordered[key] = units_mention_unified[key]

# 统一单位
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

# test.csv:
# 954,园林工人沿公路一侧植树，每隔6米种一棵，一共种100棵，从第l棵到最后一棵的距离是多少米？
# 1136,2010年5月l韪，上海世博会正式开幕.5月14日首次达到单日入园人数大约24.04万人，然而5月l5日单日入园人数创新高，比5月l4日单日入园人数还多25%，5月15日单日入园人数是多少万人?
# 1367,A型载重车有8个轮子，B型载重车有12个轮子，现有这两种载重车l7辆，共有172个轮子，求A型车有多少辆?

# 将l转换为1
def replace_l_with_1(str_):
    str_list = list(str_)
    for i, char in enumerate(str_list):
        if ((char == 'l') and (i+1 < len(str_) and ((str_[i+1] in digits) or (str_[i+1] == '.') or (str_[i+1] == ':') or (str_[i+1] == '：') or (str_[i+1] == '%') or (str_[i+1] in units_mention_unified_ordered.keys()) or (str_[i+1] in units_mention_unified_ordered.values())))) \
                or ((char == 'l') and ((i-1 >= 0) and (str_[i-1] not in digits))):
            str_list[i] = '1'
    return ''.join(str_list)

# 将1转换为l
def replace_1_with_l(str_):
    str_list = list(str_)
    for i, char in enumerate(str_list):
        if (char == '1') and (i+1 < len(str_)) and (str_[i+1] in yunmu_with_zhuyin_ext):
            str_list[i] = 'l'
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
                '({})'.format(yinjie), '')
            # 两端中文括号
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                '（{}）'.format(yinjie), '')
            # 左英右中
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                '({}）'.format(yinjie), '')
            # 左中右英
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                '（{})'.format(yinjie), '')
            # 左英
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                '({}'.format(yinjie), '')
            # 左中
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                '（{}'.format(yinjie), '')
            # 右英
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                '{})'.format(yinjie), '')
            # 右中
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                '{}）'.format(yinjie), '')
            # 原始
            question_with_yinjie_deleted = question_with_yinjie_deleted.replace(
                yinjie, '')

    return question_with_yinjie_deleted

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

# 后处理
def generate_ans_and_post_process_for_competition_format(question_cleaned, equation_infix_for_eval_ans):
    global units_mention_re
    global units_mention_re2
    if equation_infix_for_eval_ans.startswith('x='):
        equation_infix_for_eval_ans = equation_infix_for_eval_ans[2:]

    equation_for_eval_ans = equation_infix_for_eval_ans

    # 小数百分数匹配列表
    pattern_percentage_float = re.findall(
        r'(\d+\.\d+%)', equation_for_eval_ans)
    if len(pattern_percentage_float) > 0:
        pattern_percentage_float.sort(
            key=lambda x: len(x), reverse=True)

        for percentage_float in pattern_percentage_float:
            equation_for_eval_ans = equation_for_eval_ans.replace(
                percentage_float, '({}/100)'.format(percentage_float[:-1]))

    # 整数百分数匹配列表
    pattern_percentage_int = re.findall(r'(\d+%)', equation_for_eval_ans)
    if len(pattern_percentage_int) > 0:
        pattern_percentage_int.sort(
            key=lambda x: len(x), reverse=True)

        for percentage_int in pattern_percentage_int:
            equation_for_eval_ans = equation_for_eval_ans.replace(
                percentage_int, '({}/100)'.format(percentage_int[:-1]))

    equation_for_eval_ans = equation_for_eval_ans.replace('^', '**')

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

    # 条件：最后一个子句（不包括额外信息）含有“百分”的
    cond_percentage_in_last_sep = len(question_sep_by_seg_punctuations) >= 1 \
        and ('百分' in question_sep_by_seg_punctuations[-1])

    # TODO doc_index train 89 率的问题，仍然没有化为百分数
    # 条件：最后一个子句（不包括额外信息）含有“率”的，其他增加条件说明详见data_process_post.py
    cond_rate_in_last_sep = len(question_sep_by_seg_punctuations) >= 1 \
        and ('率' in question_sep_by_seg_punctuations[-1]) \
        and ('%' not in question_sep_by_seg_punctuations[-1]) \
        and ('率的' not in question_sep_by_seg_punctuations[-1])

    # 首先构造比率类关键词+问句标志词列表
    rate_keywords = ['浓度', '纯度', '盐度', '咸度', '饱和度']
    combination1_rate = ['{}是多少'.format(item) for item in rate_keywords]
    combination2_rate = ['{}为多少'.format(item) for item in rate_keywords]
    combination3_rate = ['{}多少'.format(item) for item in rate_keywords]
    combination4_rate = ['{}？'.format(item) for item in rate_keywords]
    combination5_rate = ['{}?'.format(item) for item in rate_keywords]

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

    # 首先构造比例类关键词+问句标志词列表
    ratio_keywords = ['比例', '比率', '比重', '占比']
    combination1_ratio = ['{}是多少'.format(item) for item in ratio_keywords]
    combination2_ratio = ['{}为多少'.format(item) for item in ratio_keywords]
    combination3_ratio = ['{}多少'.format(item) for item in ratio_keywords]
    combination4_ratio = ['{}？'.format(item) for item in ratio_keywords]
    combination5_ratio = ['{}?'.format(item) for item in ratio_keywords]

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

    try:
        eval_result_py = eval(equation_for_eval_ans)
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
        if (re.findall(r'多少[辆|人|个|只|箱|本|次|张|块|条]', question_sep_by_seg_punctuations[-1]) or
                re.findall(r'几[辆|人|个|只|箱|包|本|次|张|块|条]', question_sep_by_seg_punctuations[-1])):

            if re.findall(r'至少|最少|起码|租|船|拉完|运完|需要|需|要|限乘|乘坐|准乘|限载|限坐', question_sep_by_seg_punctuations[-1]) or (len(question_sep_by_seg_punctuations) > 1 and re.findall(r'只能|限乘|乘坐|准乘|限载|限坐', question_sep_by_seg_punctuations[-2])):
                ans = ceil(eval_result_py)
            elif re.findall(r'至多|最多|顶多|可以|分|能|一共', question_sep_by_seg_punctuations[-1]):
                ans = floor(eval_result_py)
            else:
                ans = int(eval_result_py+0.5)

        elif (re.findall(r'多少[圈|顶|桶]', question_sep_by_seg_punctuations[-1]) or re.findall(r'几[圈|顶|桶]', question_sep_by_seg_punctuations[-1])):

            if re.findall(r'至少|最少|起码|需要', question_sep_by_seg_punctuations[-1]):
                ans = ceil(eval_result_py)
            else:
                ans = int(eval_result_py+0.5)

        elif re.findall(r'多少[束|件|副|头|幅|排|枝|枝|根|瓶|盒|组|袋|套]', question_sep_by_seg_punctuations[-1]) or re.findall(r'几[束|件|副|头|幅|排|枝|枝|根|瓶|盒|组|袋|套]', question_sep_by_seg_punctuations[-1]):

            if re.findall(r'至多|最多|顶多|可以|能|可', question_sep_by_seg_punctuations[-1]):
                ans = floor(eval_result_py)
            else:
                ans = int(eval_result_py+0.5)

        elif re.findall(r'至少|最少|起码', question_sep_by_seg_punctuations[-1]) or (len(question_sep_by_seg_punctuations) > 1 and re.findall(r'至少|最少', question_sep_by_seg_punctuations[-2])):

            if (re.findall(units_mention_re, question_sep_by_seg_punctuations[-1]) or re.findall(units_mention_re2, question_sep_by_seg_punctuations[-1])):
                if '保留整' in last_20_chars:
                    ans = ceil(eval_result_py)
                else:
                    is_there_float_in_expr_infix = False
                    for item in expr_infix:
                        if '.' in '{}'.format(item):
                            is_there_float_in_expr_infix = True
                            break
                    if is_there_float_in_expr_infix:
                        ans = round_up(
                            eval_result_py, keep_float_bits=5)
                        if '{}'.format(ans).endswith('.0'):
                            ans = '{}'.format(ans)[:-2]
                    else:
                        ans = eval(
                            re.sub(r'([\d]+)', 'Integer(\\1)', expr_infix))
                        if '.' in '{}'.format(ans):
                            ans = round_up(eval('{}'.format(ans)), keep_float_bits=5)
                        if '{}'.format(ans).endswith('.0'):
                            ans = '{}'.format(ans)[:-2]
            else:
                ans = ceil(eval_result_py)

        elif re.findall(r'至多|最多|顶多', question_sep_by_seg_punctuations[-1]):

            if (re.findall(units_mention_re, question_sep_by_seg_punctuations[-1]) or re.findall(units_mention_re2, question_sep_by_seg_punctuations[-1])):
                if '保留整' in last_20_chars:
                    ans = floor(eval_result_py)
                else:
                    is_there_float_in_expr_infix = False
                    for item in expr_infix:
                        if '.' in '{}'.format(item):
                            is_there_float_in_expr_infix = True
                            break
                    if is_there_float_in_expr_infix:
                        ans = round_up(
                            eval_result_py, keep_float_bits=5)
                        if '{}'.format(ans).endswith('.0'):
                            ans = '{}'.format(ans)[:-2]
                    else:
                        ans = eval(
                            re.sub(r'([\d]+)', 'Integer(\\1)', expr_infix))
                        if '.' in '{}'.format(ans):
                            ans = round_up(eval('{}'.format(ans)), keep_float_bits=5)
                        if '{}'.format(ans).endswith('.0'):
                            ans = '{}'.format(ans)[:-2]
            else:
                ans = floor(eval_result_py)

        elif (len(question_sep_by_seg_punctuations) > 1) and re.findall(r'至多|最多|顶多', question_sep_by_seg_punctuations[-2]) and ('多少' not in question_sep_by_seg_punctuations[-2]):

            if (re.findall(units_mention_re, question_sep_by_seg_punctuations[-1]) or re.findall(units_mention_re2, question_sep_by_seg_punctuations[-1])):
                if '保留整' in last_20_chars:
                    ans = floor(eval_result_py)
                else:
                    ans = ceil(eval_result_py)
            else:
                ans = ceil(eval_result_py)

        elif cond_percentage_in_last_sep or cond_rate_in_last_sep or with_rate_keywords_in_last_sep:

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
                float_num_bits = '{}'.format(percentage_num).split('.')[1]
                if len(float_num_bits) < 2:
                    percentage_num = '{}0'.format(percentage_num)
            else:
                # 现改为百分号前的小数默认保留一位
                percentage_num = round_up(
                    eval_result_py * 100, keep_float_bits=1)
                if '{}'.format(percentage_num).endswith('.0'):
                    percentage_num = '{}'.format(percentage_num)[:-2]
            ans = '{}%'.format(percentage_num)

        elif cond_fraction_in_last_sep or with_ratio_keywords_in_last_sep:

            # 小数匹配列表
            pattern_float = re.findall(r'(\d+\.\d+)', expr_infix)

            if len(pattern_float) > 0:
                pattern_float.sort(key=lambda x: len(x), reverse=True)
                for _i, float_ in enumerate(pattern_float):
                    expr_infix = expr_infix.replace(
                        float_, str(Fraction(eval('{}'.format(float_))).limit_denominator()))

            ans = eval(
                re.sub(r'([\d]+)', 'Integer(\\1)', expr_infix))
            if '.' in '{}'.format(ans):
                ans = round_up(eval('{}'.format(ans)), keep_float_bits=5)
            if '{}'.format(ans).endswith('.0'):
                ans = '{}'.format(ans)[:-2]

        elif ('保留到个位' in last_20_chars) or \
            ('保留个位' in last_20_chars) or \
            ('精确到个位' in last_20_chars) or \
            ('保留整' in last_20_chars) or \
            ('精确到整' in last_20_chars) or \
            ('保留到1' in last_20_chars) or \
                ('精确到1' in last_20_chars):
            ans = int(eval_result_py+0.5)

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

        # 比例尺类问题保留小数
        elif '比例尺' in question_with_spaces_deleted:
            ans = eval_result_py
            if '.' in '{}'.format(ans):
                ans = round_up(eval('{}'.format(ans)), keep_float_bits=5)
            if '{}'.format(ans).endswith('.0'):
                ans = '{}'.format(ans)[:-2]

        else:
            is_there_float_in_expr_infix = False
            for item in expr_infix:
                if '.' in '{}'.format(item):
                    is_there_float_in_expr_infix = True
                    break
            if is_there_float_in_expr_infix:
                ans = round_up(eval_result_py, keep_float_bits=5)
                if '{}'.format(ans).endswith('.0'):
                    ans = '{}'.format(ans)[:-2]
            else:
                ans = eval(
                    re.sub(r'([\d]+)', 'Integer(\\1)', expr_infix))
                if '.' in '{}'.format(ans):
                    ans = round_up(eval('{}'.format(ans)), keep_float_bits=5)
                if '{}'.format(ans).endswith('.0'):
                    ans = '{}'.format(ans)[:-2]

    # 转为字符串
    ans = '{}'.format(ans)
    return ans
