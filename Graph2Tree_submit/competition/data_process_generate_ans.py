import csv
import os
import pickle
import pprint

from tqdm import tqdm

from data_process_utils import (
    char_unify_convertor, convert_cn_colon_to_en, convert_en_punct_to_cn,
    convert_some_mentions, del_spaces,
    generate_ans_and_post_process_for_competition_format,
    parse_and_eval_prefix_expr, replace_1_with_l, replace_l_with_1,
    rm_pinyin_yinjie, units_mention_unify)

# generated_path = './generated/graph2tree_competition_eda_0_operator_no_gt_4/predicted_list.pkl'
# generated_path = './generated/graph2tree_competition_eda_1_operator_no_gt_4/predicted_list.pkl'
# generated_path = './generated/graph2tree_competition_eda_2_operator_no_gt_4/predicted_list.pkl'
# generated_path = './generated/graph2tree_competition_eda_3_operator_no_gt_4/predicted_list.pkl'
# generated_path = './generated/graph2tree_competition_eda_4_operator_no_gt_4/predicted_list.pkl'
# generated_path = './generated/graph2tree_competition_eda_5_operator_no_gt_4/predicted_list.pkl'
# generated_path = './generated/graph2tree_competition_eda_6_operator_no_gt_4_epoches_70/predicted_list.pkl'
# generated_path = './generated/graph2tree_competition_eda_7_operator_no_gt_4/predicted_list.pkl'
generated_path = './generated/graph2tree_competition_eda_8_operator_no_gt_4_epoches_60/predicted_list.pkl'
# generated_path = './generated/graph2tree_competition_eda_9_operator_no_gt_4/predicted_list.pkl'


predicted_list = pickle.load(open(generated_path, 'rb'))

print('what the first 10 items of predicted_list are:')
# pprint.pprint(predicted_list[:10])
print('and the last item of predicted_list is:')
# pprint.pprint(predicted_list[-1])
print('and its original length is:')
pprint.pprint(len(predicted_list))
print()


if os.path.exists('../submits/submit.csv'):
    os.system('rm -rf "../submits/submit.csv"')

if not os.path.exists('../submits/submit.csv'):
    test_submit_f = open(
        '../submits/submit.csv', 'w', encoding='utf-8')
    csv_writer_submit = csv.writer(test_submit_f)


with open('../official_data/test.csv', 'r') as f:
    reader = csv.reader(f)

    counter_all \
        = counter_model_cannot_predict \
        = counter_prefix_expr_not_startswith_operator \
        = counter_compute_prefix_expression_func_none \
        = counter_parsed_tree_with_multi_leaves \
        = counter_discrepency_between_evalution \
        = counter_division_by_zero \
        = 0

    # for row in tqdm(reader):
    for doc_index, row in tqdm(enumerate(reader)):
        # print(row)

        if len(predicted_list[doc_index]['prefix_expr']) > 0:

            question = row[1]

            # 预处理的第一步，先把问题句子中多余的空格去掉，避免影响判断
            # 比赛数据集特有的，再把'|','$','·'去掉
            question = del_spaces(row[1]).replace(
                '|', '').replace('$', '').replace('·', '')
            # 再把两端多余的空格去掉
            question = question.strip()
            # print(question)

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

            question_with_spaces_deleted = question

            try:

                # print(
                #     f'for doc_index: {doc_index}, what the prefix_expr is: ')
                # pprint.pprint(predicted_list[doc_index]['prefix_expr'])
                # print()

                eval_result_py, expr_infix, add_info = parse_and_eval_prefix_expr(
                    predicted_list[doc_index]['prefix_expr'])

                if add_info.startswith('prefix_expr_list[0] is not an operator'):
                    counter_prefix_expr_not_startswith_operator += 1
                    ans = -1000
                elif add_info.startswith('the compute_prefix_expression() result is now None'):
                    counter_compute_prefix_expression_func_none += 1
                    ans = -1000
                else:

                    ans = generate_ans_and_post_process_for_competition_format(
                        question_with_spaces_deleted, expr_infix)

                """
                # 上面是比赛最终提交时使用的逻辑，逻辑瑕疵
                # TODO 上面应该注掉，应该将这部分打开！！！即出现“老求解器”无法求解出结果的，只计数即可，转而使用“新求解器”求解就好，
                # 而不必直接给出-1000的答案，这样会提前放弃了使用“新求解器”求出正确答案的可能性。
                if add_info.startswith('the compute_prefix_expression() result is now None'):
                    counter_compute_prefix_expression_func_none += 1

                if add_info.startswith('prefix_expr_list[0] is not an operator'):
                    counter_prefix_expr_not_startswith_operator += 1
                    ans = -1000
                else:
                    ans = generate_ans_and_post_process_for_competition_format(
                        question_with_spaces_deleted, expr_infix)
                """

            except Exception as e:

                if 'has multiple leaves' in f'{e}':
                    counter_parsed_tree_with_multi_leaves += 1
                elif f'{e}'.startswith('discrepency found between'):
                    counter_discrepency_between_evalution += 1
                elif 'division by zero' in f'{e}':
                    counter_division_by_zero += 1

                ans = -1000

        else:
            # print('由于模型无法生成该题的前置运算符表达式，故无法用前置运算符表达式解析器求解，答案暂给-1000\n')
            counter_model_cannot_predict += 1
            ans = -1000

        csv_writer_submit.writerow([row[0], ans])

        if 'doc_index' not in dir():
            counter_all += 1

    if 'doc_index' in dir():
        counter_all = doc_index + 1

print(
    f'test stats: counter_all: {counter_all}')
print(
    f'test stats: model cannot predict: {counter_model_cannot_predict}, percentage: {counter_model_cannot_predict/counter_all}')
print(
    f'test stats: the predicted prefix expr not started with an operator: {counter_prefix_expr_not_startswith_operator}, percentage: {counter_prefix_expr_not_startswith_operator/counter_all}')
print(
    f'test stats: the provided compute_prefix_expression() on the predicted prefix expr returns None: {counter_compute_prefix_expression_func_none}, percentage: {counter_compute_prefix_expression_func_none/counter_all}')
print(
    f'test stats: the parsed tree with multi leaves: {counter_parsed_tree_with_multi_leaves}, percentage: {counter_parsed_tree_with_multi_leaves/counter_all}')
print(
    f'test stats: discrepency found between parse_and_eval_prefix_expr() and the provided compute_prefix_expression(): {counter_discrepency_between_evalution}, percentage: {counter_discrepency_between_evalution/counter_all}')
print(
    f'test stats: division by zero found: {counter_division_by_zero}, percentage: {counter_division_by_zero/counter_all}')
print()
