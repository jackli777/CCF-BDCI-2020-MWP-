import copy
import csv
import json
import pprint
import re
from string import ascii_letters, digits

from tqdm import tqdm
from w3lib.html import remove_tags

# from data_process_timeout import null_callback, time_out
from data_process_utils import (
    char_unify_convertor, contains_cn_chars, convert_cn_colon_to_en,
    convert_en_punct_to_cn, convert_mixed_num_to_fraction_for_graph2tree,
    convert_some_mentions, del_add_info, del_cn_en_punctuations, del_spaces,
    find_lcsubstr, generate_ans_and_post_process_for_competition_format,
    generate_num_list, replace_1_with_l, replace_l_with_1, rm_pinyin_yinjie,
    round_up, sep_by_seg_punctuations, units_mention_unify)

file_name_raw = 'items_zybang_train_raw.json'

scrapy_results_path = f'./generated/scrapy_processed/{file_name_raw}'

scrapy_results = json.load(open(scrapy_results_path, 'r'))
scrapy_results.sort(key=lambda x: x['doc_index'])

print('what the scrapy_results is:')
# pprint.pprint(scrapy_results)
print('and its length is:')
pprint.pprint(len(scrapy_results))
print()

range_to_process = max(
    list(map(lambda x: x['doc_index'], scrapy_results))) + 1

print('what the range_to_process is:')
pprint.pprint(range_to_process)
print()


def process_fraction_nums(str_, fraction_nums_list):
    for fraction_num in fraction_nums_list:

        fraction_nums_pattern = re.findall(
            r'\>(\d+)\<\/td\>\<\/tr\>', fraction_num)

        if len(fraction_nums_pattern) > 0:
            str_ = str_.replace(fraction_num, '(' + '/'.join(
                fraction_nums_pattern) + ')')

    return str_


def process_break_line(str_):
    return str_ \
        .replace('\r\n', '<br>') \
        .replace('\n', '<br>') \
        .replace('\t', '<br>') \
        .replace('       ', '<br>') \
        .replace('      ', '<br>') \
        .replace('     ', '<br>') \
        .replace('    ', '<br>') \
        .replace('   ', '<br>') \
        .split('<br>')


def del_cn_en_char(str_):
    str_ret = ''
    for char in str_:
        if ('\u4e00' <= char <= '\u9fff') or (char == '：') or (char in set(ascii_letters).difference('xXyY')):
            pass
        else:
            str_ret += char
    return str_ret


def rm_null_brackets(str_):

    str_list = list(str_)

    if str_.startswith('1)') or \
            str_.startswith('2)') or \
            str_.startswith('3)') or \
            str_.startswith('4)') or \
            str_.startswith('5)') or \
            str_.startswith('6)') or \
            str_.startswith('7)') or \
            str_.startswith('8)') or \
            str_.startswith('9)') or \
            str_.startswith('1）') or \
            str_.startswith('2）') or \
            str_.startswith('3）') or \
            str_.startswith('4）') or \
            str_.startswith('5）') or \
            str_.startswith('6）') or \
            str_.startswith('7）') or \
            str_.startswith('8）') or \
            str_.startswith('9）') or \
            str_.startswith('1】') or \
            str_.startswith('2】') or \
            str_.startswith('3】') or \
            str_.startswith('4】') or \
            str_.startswith('5】') or \
            str_.startswith('6】') or \
            str_.startswith('7】') or \
            str_.startswith('8】') or \
            str_.startswith('9】'):
        str_list = str_list[2:]

    elif (str_.startswith('1.') or
            str_.startswith('2.') or
            str_.startswith('3.') or
            str_.startswith('4.') or
            str_.startswith('5.') or
            str_.startswith('6.') or
            str_.startswith('7.') or
            str_.startswith('8.') or
            str_.startswith('9.') or
            str_.startswith('1,') or
            str_.startswith('2,') or
            str_.startswith('3,') or
            str_.startswith('4,') or
            str_.startswith('5,') or
            str_.startswith('6,') or
            str_.startswith('7,') or
            str_.startswith('8,') or
            str_.startswith('9,') or
            str_.startswith('1、') or
            str_.startswith('2、') or
            str_.startswith('3、') or
            str_.startswith('4、') or
            str_.startswith('5、') or
            str_.startswith('6、') or
            str_.startswith('7、') or
            str_.startswith('8、') or
            str_.startswith('9、')) and \
            (len(str_) > 2) and \
            (str_[2] not in digits):
        str_list = str_list[2:]

    str_ = ''.join(str_list)

    return str_ \
        .replace('(1)', '') \
        .replace('(2)', '') \
        .replace('(3)', '') \
        .replace('(4)', '') \
        .replace('(5)', '') \
        .replace('(6)', '') \
        .replace('(7)', '') \
        .replace('(8)', '') \
        .replace('(9)', '') \
        .replace('（1）', '') \
        .replace('（2）', '') \
        .replace('（3）', '') \
        .replace('（4）', '') \
        .replace('（5）', '') \
        .replace('（6）', '') \
        .replace('（7）', '') \
        .replace('（8）', '') \
        .replace('（9）', '') \
        .replace('【1】', '') \
        .replace('【2】', '') \
        .replace('【3】', '') \
        .replace('【4】', '') \
        .replace('【5】', '') \
        .replace('【6】', '') \
        .replace('【7】', '') \
        .replace('【8】', '') \
        .replace('【9】', '') \
        .replace('()', '') \
        .replace('（）', '') \
        .replace('【】', '')


def unify_brackets(str_):
    return str_ \
        .replace('（', '(') \
        .replace('）', ')') \
        .replace('﹙', '(') \
        .replace('﹚', ')') \
        .replace('[', '(') \
        .replace(']', ')') \
        .replace('【', '(') \
        .replace('】', ')') \
        .replace('{', '(') \
        .replace('}', ')') \
        .replace('〔', '(') \
        .replace('〕', ')') \
        .replace('❨', '(') \
        .replace('❩', ')') \
        .replace('❪', '(') \
        .replace('❫', ')') \
        .replace('❴', '(') \
        .replace('❵', ')') \
        .replace('❲', '(') \
        .replace('❳', ')') \
        .replace('⎨', '(') \
        .replace('⎬', ')') \
        .replace('〖', '(') \
        .replace('〗', ')')


# doc_index_to_inspect = 7970
for i, scrapy_result in enumerate(tqdm(scrapy_results)):

    if ('question_searched' in scrapy_result.keys()) and (len(scrapy_result['question_searched']) > 0) and ('des' in scrapy_result.keys()) and (scrapy_result['des'] != '占位问题'):

        question_searched_list = process_break_line(
            scrapy_result['question_searched'][0])

        fraction_nums_question = scrapy_result['fraction_nums_question']

        if len(fraction_nums_question) > 0:

            question_searched_list = list(
                map(lambda x: process_fraction_nums(x, fraction_nums_question), question_searched_list))

        question_searched_cleaned_list = list(map(lambda x: re.sub(
            r'[\t\r\n\s]', '', remove_tags(x)), question_searched_list))
        question_searched_cleaned_list = list(
            filter(lambda x: x.strip() != '', question_searched_cleaned_list))

    else:
        question_searched_cleaned_list = []

    scrapy_results[i]['question_searched_cleaned_list'] = question_searched_cleaned_list
    question_searched_cleaned_str = ''.join(question_searched_cleaned_list)
    question_competition_preprocessed = scrapy_result['title_question']

    # 先把空格删去
    question_searched_cleaned_str = del_spaces(question_searched_cleaned_str)
    # 再把两端多余的空格去掉
    question_searched_cleaned_str = question_searched_cleaned_str.strip()
    # print(question_searched_cleaned_str)

    # 符号字符统一
    question_searched_cleaned_str = char_unify_convertor(
        question_searched_cleaned_str)

    # 将一些写错的l替换为1
    question_searched_cleaned_str = replace_l_with_1(
        question_searched_cleaned_str)

    # 将一些写错的1替换为l
    question_searched_cleaned_str = replace_1_with_l(
        question_searched_cleaned_str)

    # 改用封装后的函数，删除拼音音节
    question_searched_cleaned_str = rm_pinyin_yinjie(
        question_searched_cleaned_str)

    # 改用封装后的函数，单位表述进行统一
    question_searched_cleaned_str = units_mention_unify(
        question_searched_cleaned_str)

    # 改用封装后的函数，超过1个字符的表述替换
    question_searched_cleaned_str = convert_some_mentions(
        question_searched_cleaned_str)

    # 求LCS的时候，先把所有标点都去掉：
    lcs_result = find_lcsubstr(
        del_cn_en_punctuations(question_searched_cleaned_str), del_spaces(del_cn_en_punctuations(question_competition_preprocessed)))
    lcs = lcs_result[0]
    lcs_len = lcs_result[1]

    """
    if scrapy_result['doc_index'] == doc_index_to_inspect:
        print(f'for doc_index {doc_index_to_inspect}, lcs is: {lcs}')
        print(f'for doc_index {doc_index_to_inspect}, lcs_len is: {lcs_len}')
        print()
    """

    scrapy_results[i]['lcs'] = lcs
    scrapy_results[i]['lcs_len'] = lcs_len

scrapy_results_grouped = []
scrapy_results_lcs = []

for i in range(range_to_process):

    current_group = list(filter(lambda x: x['doc_index'] == i, scrapy_results))

    for j, item in enumerate(current_group):
        if item['is_best_ans']:
            current_group[j]['is_best_ans'] = 1
        else:
            current_group[j]['is_best_ans'] = 0

    if len(current_group) > 0:
        current_group.sort(key=lambda x: (x['lcs_len'], x['is_best_ans'], 0-len(
            ''.join(x['question_searched_cleaned_list']))), reverse=True)
        scrapy_results_grouped.append(current_group)
        scrapy_results_lcs.append(current_group[0])
    else:
        scrapy_results_grouped.append([{'doc_index': i}])
        scrapy_results_lcs.append({'doc_index': i})

# print('what the scrapy_results_grouped is:')
# pprint.pprint(scrapy_results_grouped)
# print('and its length is:')
# pprint.pprint(len(scrapy_results_grouped))
# print()

assert len(scrapy_results_grouped) == range_to_process

# print('what the scrapy_results_lcs is:')
# pprint.pprint(scrapy_results_lcs)
# print('and its length is:')
# pprint.pprint(len(scrapy_results_lcs))
# print()

assert len(scrapy_results_lcs) == range_to_process

for i, scrapy_result in enumerate(tqdm(scrapy_results_lcs)):

    if 'title_question' in scrapy_result.keys():
        question_with_spaces_deleted = scrapy_result['title_question']

        # 之前第一步“搜”已经做了一些预处理，这里把后面从已有数据集中进行匹配用的预处理补上：

        # 将英文标点转为中文
        question_with_spaces_deleted = convert_en_punct_to_cn(
            question_with_spaces_deleted)

        # 统一将带分数化为假分数
        question_with_spaces_deleted = convert_mixed_num_to_fraction_for_graph2tree(
            question_with_spaces_deleted)

        # 分数去括号
        question_with_spaces_deleted = re.sub(
            r'\((\d+/\d+)\)', '\\1', question_with_spaces_deleted)
    else:
        question_with_spaces_deleted = ''

    if ('calculation_procedures' in scrapy_result.keys()) and (len(scrapy_result['calculation_procedures']) > 0) and ('des' in scrapy_result.keys()) and (scrapy_result['des'] != '占位问题'):

        # calculation_procedures = scrapy_result['calculation_procedures'][0].replace(
        #     '\r\n', '<br>').replace('\n', '<br>').split('<br>')
        calculation_procedures_list = process_break_line(
            scrapy_result['calculation_procedures'][0])

        fraction_nums_cal = scrapy_result['fraction_nums_cal']

        if len(fraction_nums_cal) > 0:

            # calculation_procedures = process_fraction_nums(
            #     calculation_procedures, fraction_nums_cal)

            calculation_procedures_list = list(
                map(lambda x: process_fraction_nums(x, fraction_nums_cal), calculation_procedures_list))

        # calculation_procedures_cleaned = re.sub(
        #     r'[\t\r\n\s]', '', remove_tags(calculation_procedures))

        calculation_procedures_cleaned_list = list(map(lambda x: re.sub(
            r'[\t\r\n\s]', '', remove_tags(x)), calculation_procedures_list))
        # calculation_procedures_cleaned_list 中的每个成员还得按seg_punct断句
        calculation_procedures_cleaned_list_ = list(
            map(lambda x: sep_by_seg_punctuations(x), calculation_procedures_cleaned_list))
        calculation_procedures_cleaned_list = []
        for item in calculation_procedures_cleaned_list_:
            calculation_procedures_cleaned_list.extend(item)
        calculation_procedures_cleaned_list = list(
            filter(lambda x: x.strip() != '', calculation_procedures_cleaned_list))

    else:
        # calculation_procedures_cleaned = ''
        calculation_procedures_cleaned_list = []

    # print('calculation_procedures_cleaned is:')
    # pprint.pprint(calculation_procedures_cleaned)
    # print()

    # scrapy_results_lcs[i]['calculation_procedures_cleaned'] = calculation_procedures_cleaned
    scrapy_results_lcs[i]['calculation_procedures_cleaned_list'] = calculation_procedures_cleaned_list

    # calculation_procedures_cleaned_list只有一个成员的，尝试提取ans，
    # equation走后续流程，无论calculation_procedures_cleaned_list是否只有一个成员
    # "doc_index": 16 55 64 85 90 100 110 112 118 121 143 157 159 176 179 187 192
    if len(calculation_procedures_cleaned_list) == 1:
        # print(i, calculation_procedures_cleaned_list)

        ans_maybe = calculation_procedures_cleaned_list[0]
        ans_maybe = del_spaces(ans_maybe)
        ans_maybe = char_unify_convertor(ans_maybe)

        # 括号替换补全！！！
        ans_maybe = unify_brackets(ans_maybe)

        if '=' in ans_maybe:
            ans_maybe = ans_maybe.split('=')[-1]

        ans = ''
        found_ans_char = False
        for char in ans_maybe:
            if (char in digits) or (char == '%') or (char == '.') or (char == '．') or (char == '/'):
                found_ans_char = True
                ans += char
            else:
                if found_ans_char:
                    break
                else:
                    continue

        # print(i, ans)

    else:
        # doc_index_to_inspect = 3

        ans = ''
        for ans_maybe_line in calculation_procedures_cleaned_list[::-1]:

            # if scrapy_result['doc_index'] == doc_index_to_inspect:
            #     print('ans_maybe_line:')
            #     pprint.pprint(ans_maybe_line)
            #     print()

            if ans_maybe_line.startswith('答：'):
                num_list = generate_num_list(
                    ans_maybe_line, for_scraper=True)['num_list']

                # if scrapy_result['doc_index'] == doc_index_to_inspect:
                #     print('num_list:')
                #     pprint.pprint(num_list)
                #     print()

                if len(num_list) > 0:
                    ans = num_list[-1]
                    break

        # if scrapy_result['doc_index'] == doc_index_to_inspect:
        #     print('ans:')
        #     pprint.pprint(ans)
        #     print()

        if ans == '':
            for ans_maybe_line in calculation_procedures_cleaned_list[::-1]:
                if ans_maybe_line.startswith('故答案为：'):
                    num_list = generate_num_list(
                        ans_maybe_line, for_scraper=True)['num_list']
                    if len(num_list) > 0:
                        ans = num_list[-1]
                        break

    equation = ''
    # doc_index_to_inspect = 26
    for equation_maybe_line in calculation_procedures_cleaned_list:

        # 直接看数字占比（绝对数量，如2） doc_index 62 doc_index 108是反例，但是正确的
        if len(calculation_procedures_cleaned_list) > 1:
            count_num = 0
            equation_maybe_line_for_count_num = equation_maybe_line
            equation_maybe_line_for_count_num = equation_maybe_line_for_count_num.replace(
                '3.14', 'π')
            for char in equation_maybe_line_for_count_num:
                if (char in digits) or (char == 'π'):
                    count_num += 1
            if count_num < 2:
                continue

        # 判断该行是否有比例符号
        # doc_index 110
        found_ratio_sign = False
        for j, char in enumerate(equation_maybe_line):
            if (char in ':：﹕∶︰') \
                    and (j != len(equation_maybe_line) - 1) \
                    and (j != 0) \
                    and (j+1 < len(equation_maybe_line)) \
                    and (equation_maybe_line[j+1] in digits) \
                    and (j-1 >= 0) \
                    and (equation_maybe_line[j-1] in digits):
                found_ratio_sign = True
                break

        if found_ratio_sign:
            continue

        equation_maybe_line = equation_maybe_line.replace(
            '加上', '+').replace('减去', '-').replace('乘以', '*').replace('除以', '/')

        # if scrapy_result['doc_index'] == doc_index_to_inspect:
        #     print('equation_maybe_line at #1')
        #     pprint.pprint(equation_maybe_line)
        #     print()

        equation_maybe_line = del_cn_en_char(equation_maybe_line)

        # if scrapy_result['doc_index'] == doc_index_to_inspect:
        #     print('equation_maybe_line at #2')
        #     pprint.pprint(equation_maybe_line)
        #     print()

        equation_maybe_line = del_spaces(equation_maybe_line)

        # if scrapy_result['doc_index'] == doc_index_to_inspect:
        #     print('equation_maybe_line at #3')
        #     pprint.pprint(equation_maybe_line)
        #     print()

        equation_maybe_line = char_unify_convertor(equation_maybe_line)

        equation_maybe_line = unify_brackets(equation_maybe_line)

        # if scrapy_result['doc_index'] == doc_index_to_inspect:
        #     print('equation_maybe_line at #4')
        #     pprint.pprint(equation_maybe_line)
        #     print()

        equation_maybe_line = del_cn_en_punctuations(equation_maybe_line)

        # if scrapy_result['doc_index'] == doc_index_to_inspect:
        #     print('equation_maybe_line at #5')
        #     pprint.pprint(equation_maybe_line)
        #     print()

        equation_maybe_line = rm_null_brackets(equation_maybe_line)

        # if scrapy_result['doc_index'] == doc_index_to_inspect:
        #     print('equation_maybe_line at #6')
        #     pprint.pprint(equation_maybe_line)
        #     print()

        # 发现的幂运算符号数量：
        found_power_sign_pattern1 = re.findall(
            r'([\d+|\)]?\*\*[\d+|\(])', equation_maybe_line)
        found_power_sign_pattern2 = re.findall(
            r'([\d+|\)]?\^[\d+|\(])', equation_maybe_line)

        amount_power_signs = len(found_power_sign_pattern1) + \
            len(found_power_sign_pattern1)

        # 发现的幂运算符号数量，超过两个的时候直接break，不用进行后续过程！！！
        if amount_power_signs > 2:
            break

        # 先将表示乘号的xX转为乘号
        equation_maybe_line_list = list(equation_maybe_line)
        for j, char in enumerate(equation_maybe_line_list):
            if ((char == 'x') or (char == 'X')) \
                    and (j != len(equation_maybe_line_list) - 1) \
                    and (j != 0) \
                    and (j+1 < len(equation_maybe_line_list)) \
                    and ((equation_maybe_line_list[j+1] in digits) or (equation_maybe_line_list[j+1] == '(')) \
                    and (j-1 >= 0) \
                    and ((equation_maybe_line_list[j-1] in digits) or (equation_maybe_line_list[j-1] == ')') or (equation_maybe_line_list[j-1] == '%')):
                equation_maybe_line_list[j] = '*'
        equation_maybe_line = ''.join(equation_maybe_line_list)

        # 有方程直接break，不用后续！！！
        if ('x' in equation_maybe_line) \
                or ('X' in equation_maybe_line) \
                or ('y' in equation_maybe_line) \
                or ('Y' in equation_maybe_line):
            break

        if equation_maybe_line.startswith('='):
            equation_maybe_line = equation_maybe_line[1:]

        if (len(equation_maybe_line) > 0) \
                and (equation_maybe_line[0] in digits or equation_maybe_line[0] == '(') \
                and (('+' in equation_maybe_line) or ('-' in equation_maybe_line) or ('*' in equation_maybe_line) or ('/' in equation_maybe_line) or ('^' in equation_maybe_line) or ('**' in equation_maybe_line)):
            if '=' in equation_maybe_line:
                equation = equation_maybe_line.split('=')[0]
            else:
                equation = equation_maybe_line
            break

    if (ans != '') \
            and (('+' in ans)
                 or ('-' in ans)
                 or ('*' in ans)
                 #  or ('/' in ans) # 这个不足以判断，因为可能是分数！
                 or ('^' in ans)
                 or ('**' in ans)
                 or (':' in ans)):
        ans = ''

    if (ans != '') \
            and ('0' not in ans) \
            and ('1' not in ans) \
            and ('2' not in ans) \
            and ('3' not in ans) \
            and ('4' not in ans) \
            and ('5' not in ans) \
            and ('6' not in ans) \
            and ('7' not in ans) \
            and ('8' not in ans) \
            and ('9' not in ans):
        ans = ''

    if (ans != '') and (ans.endswith('.') or ans.endswith('．')):
        ans = ans[:-1]

    ans = ans.replace('.%', '%').replace('．%', '%')

    if (equation != '') \
            and ('+' not in equation) \
            and ('-' not in equation) \
            and ('*' not in equation) \
            and ('/' not in equation) \
            and ('^' not in equation) \
            and ('**' not in equation):
        equation = ''

    if equation != '':
        equation = equation.replace('．', '.').replace(
            'π', '3.14').replace(')(', ')*(')

    # print(i, ans)

    if ((equation != '') and (ans == '')) or (('+' in ans) or ('-' in ans) or ('*' in ans) or ('**' in ans) or ('^' in ans)):
        # print(i, equation)
        # 能拿到equation，但是没有ans的，也要eval出ans

        if (equation != '') and (ans == ''):
            equation_for_eval_ans = equation
        elif ('+' in ans) or ('-' in ans) or ('*' in ans) or ('**' in ans) or ('^' in ans):
            equation_for_eval_ans = ans

        try:
            # doc_index_to_inspect=14 if scrapy_result["doc_index"] == 14 else -1
            # doc_index_to_inspect=scrapy_result['doc_index']
            ans = generate_ans_and_post_process_for_competition_format(
                question_with_spaces_deleted, equation_for_eval_ans)
        except:
            print(
                f'for doc_index: {scrapy_result["doc_index"]}, found exception, now the question_with_spaces_deleted is:')
            pprint.pprint(question_with_spaces_deleted)
            print('and the equation_for_eval_ans is:')
            pprint.pprint(equation_for_eval_ans)
            print()
            ans = ''

        # print(i, equation, ans)

    if equation != '':
        equation = 'x=' + equation

    scrapy_results_lcs[i]['ans_crawled'] = ans
    scrapy_results_lcs[i]['equation_crawled'] = equation

    # 最后一定要清空！！！
    ans = equation = equation_for_eval_ans = ''
    eval_result_py = ''
    calculation_procedures_cleaned_list = []

# print('what the scrapy_results_lcs is after cleaned:')
# pprint.pprint(scrapy_results_lcs)
# print('and its length is:')
# pprint.pprint(len(scrapy_results_lcs))
# print()

json.dump(scrapy_results_lcs, open(file_name_raw.replace(
    'raw', 'processed'), 'w'), ensure_ascii=False)
