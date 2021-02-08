import copy
import csv
import os
import pprint

from data_process_utils import contains_non_legal_ans_chars

# B榜总排名：
# 注释中含有【，mod】的，是撰写文档时修正的“逻辑瑕疵”生成的新文件，不带【，mod】的，时B榜提交时真正用来融合的
file_1 = '../from_seq2seq/B/train_robertlarge_eda4_op4.csv'
file_2 = '../from_seq2seq/B/train_eda7_op4_robert_newpost.csv'
file_3 = '../submits/submit.csv.B榜投票融合：eda3'
# file_3 = '../submits/submit.csv.B榜投票融合：eda3，mod'
file_4 = '../submits/submit.csv.B榜投票融合：eda4'
# file_4 = '../submits/submit.csv.B榜投票融合：eda4，mod'
file_5 = '../submits/submit.csv.B榜投票融合：eda5'
# file_5 = '../submits/submit.csv.B榜投票融合：eda5，mod'
file_6 = '../from_seq2seq/B/train_eda6_op4_robert_newpost.csv'
file_7 = '../submits/submit.csv.B榜投票融合：eda1'
# file_7 = '../submits/submit.csv.B榜投票融合：eda1，mod'
file_8 = '../from_seq2seq/B/train_eda4_op4_robert_newpost.csv'
file_9 = '../submits/submit.csv.B榜投票融合：eda7'
# file_9 = '../submits/submit.csv.B榜投票融合：eda7，mod'
file_10 = '../from_seq2seq/B/train_eda3_op4_robert_newpost.csv'
# file_11 = '../submits/submit.csv.B榜投票融合：eda9'
# file_11 = '../submits/submit.csv.B榜投票融合：eda9，mod'
file_12 = '../submits/submit.csv.B榜投票融合：eda2'
# file_12 = '../submits/submit.csv.B榜投票融合：eda2，mod'
file_13 = '../submits/submit.csv.B榜投票融合：eda0'
# file_13 = '../submits/submit.csv.B榜投票融合：eda0，mod'
file_14 = '../from_seq2seq/B/train_eda5_gt4_robert_newpost.csv'
# file_15 = '../submits/submit.csv.B榜投票融合：eda6，70epoches'
# file_15 = '../submits/submit.csv.B榜投票融合：eda6，70epoches，mod'
file_16 = '../from_seq2seq/B/train_eda3_op4_bert_newpost.csv'
# file_17 = '../submits/submit.csv.B榜投票融合：eda8，60epoches'
# file_17 = '../submits/submit.csv.B榜投票融合：eda8，60epoches，mod'
file_18 = '../from_seq2seq/B/train_eda3_gt4_robert_bs20_newpost.csv'
# file_19 = '../from_ho_ho/B/train_eda6_op4_bert_newpost.csv'
# file_20 = '../from_ho_ho/B/train_eda5_gt4_bert_newpost.csv'
# file_21 = '../from_ho_ho/B/train_eda7_op4_bert_newpost.csv'

# B榜总排名，单模先验排名分，单模成绩优者，排名分高：
merge_list = [
    (file_1, 500, 'train_robertlarge_eda4_op4'),
    (file_2, 490, 'train_eda7_op4_robert_newpost'),
    (file_3, 480, 'g2t_eda3_opt4'),
    (file_4, 470, 'g2t_eda4_opt4'),
    (file_5, 460, 'g2t_eda5_opt4'),
    (file_6, 450, 'train_eda6_op4_robert_newpost'),
    (file_7, 440, 'g2t_eda1_opt4'),
    (file_8, 430, 'train_eda4_op4_robert_newpost'),
    (file_9, 420, 'g2t_eda7_opt4'),
    (file_10, 410, 'train_eda3_op4_robert_newpost'),
    # (file_11, 400, 'g2t_eda9_opt4'),
    (file_12, 390, 'g2t_eda2_opt4'),
    (file_13, 380, 'g2t_eda0_opt4'),
    (file_14, 370, 'train_eda5_gt4_robert_newpost'),
    # (file_15, 360, 'g2t_eda6_opt4_epoches_70'),
    (file_16, 350, 'train_eda3_op4_bert_newpost'),
    # (file_17, 340, 'g2t_eda8_opt4_epoches_60'),
    (file_18, 330, 'train_eda3_gt4_robert_bs20_newpost'),
    # (file_19, 320, 'train_eda6_op4_bert_newpost'),
    # (file_20, 310, 'train_eda5_gt4_bert_newpost'),
    # (file_21, 300, 'train_eda7_op4_bert_newpost'),
]


def is_legal_ans(ans):
    return ((not ans.startswith('-'))
            and ('e' not in ans)
            and (not ans.endswith('%'))
            and (not contains_non_legal_ans_chars(ans))
            and (ans.strip() != '')) \
        or ((not ans.startswith('-'))
            and (not contains_non_legal_ans_chars(ans))
            and (ans.endswith('%')
                 and (0 < eval(ans[:-1]) <= 100)))


def votes_all_from_filter(list_, filter_='g2t', votes_thresh=2):
    if len(list_) >= votes_thresh:
        all_from = True
        for item in list_:
            if not item.startswith(filter_):
                all_from = False
                break
            else:
                continue
    else:
        all_from = False
    return all_from


ans_dict_list = []
ans_dict_temp = {}
ans_dict_vote = {}
for file_ in merge_list:
    file_path = file_[0]
    file_rank_score = file_[1]
    model_config = file_[2]
    ans_dict = copy.deepcopy(ans_dict_temp)
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            ans_dict[row[0]] = {
                'ans': row[1],
                'rank_score': file_rank_score,
                'model_config': model_config,
            }
            if row[0] not in ans_dict_vote.keys():
                ans_dict_vote[row[0]] = []
    ans_dict_list.append(ans_dict)

# print('what the ans_dict_list is:')
# pprint.pprint(ans_dict_list)
# print()

# print('what the ans_dict_vote is:')
# pprint.pprint(ans_dict_vote)
# print()

for doc_index in ans_dict_vote:
    for ans_dict in ans_dict_list:
        ans_dict_vote[doc_index].append(ans_dict[doc_index])

# print('what the ans_dict_vote is at #2:')
# pprint.pprint(ans_dict_vote)
# print()

ans_dict_vote_sorted = []
ans_dict_grouped_temp = {}
# ans_dict_grouped_detail_temp = {'votes': 0, 'rank_score': -1000, }

for doc_index in ans_dict_vote:
    ans_dict_grouped = copy.deepcopy(ans_dict_grouped_temp)
    for ans_dict in ans_dict_vote[doc_index]:

        # ans_dict_grouped[ans_dict['ans']] = copy.deepcopy(
        #     ans_dict_grouped_detail_temp)
        # ans_dict_grouped[ans_dict['ans']] = {'votes': 0, 'rank_score': -1000, }

        # print('what the ans_dict is')
        # pprint.pprint(ans_dict)
        # print()

        if ans_dict['ans'] not in ans_dict_grouped.keys():
            ans_dict_grouped[ans_dict['ans']] = {
                'votes': 0,
                'votes_source': [],
                'rank_score': -1000,
                'model_config': 'model_config_temp',
            }

        # print('what the ans_dict_grouped is now at #1')
        # pprint.pprint(ans_dict_grouped)
        # print()

        if ans_dict['rank_score'] > ans_dict_grouped[ans_dict['ans']]['rank_score']:
            ans_dict_grouped[ans_dict['ans']
                             ]['rank_score'] = ans_dict['rank_score']
            ans_dict_grouped[ans_dict['ans']
                             ]['model_config'] = ans_dict['model_config']

        if is_legal_ans(ans_dict['ans']):

            if ans_dict['ans'].endswith('%'):
                if 0 <= eval(ans_dict['ans'][:-1]) <= 100:
                    # print('here 1\n!')
                    ans_dict_grouped[ans_dict['ans']]['votes'] += 1
                    ans_dict_grouped[ans_dict['ans']]['votes_source'].append(
                        ans_dict['model_config'])
                else:
                    pass
            else:

                # print('here 1\n!')

                # print('what the ans_dict_grouped is now at #3')
                # pprint.pprint(ans_dict_grouped)
                # print()

                ans_dict_grouped[ans_dict['ans']]['votes'] += 1
                ans_dict_grouped[ans_dict['ans']]['votes_source'].append(
                    ans_dict['model_config'])

                # print('what the ans_dict_grouped is now at #4')
                # pprint.pprint(ans_dict_grouped)
                # print()

        else:
            # print('here 2\n!')
            pass

        # print('what the ans_dict_grouped is now at #2')
        # pprint.pprint(ans_dict_grouped)
        # print()

    ans_dict_grouped_list = list(ans_dict_grouped.items())

    # print('what the ans_dict_grouped_list is now')
    # pprint.pprint(ans_dict_grouped_list)
    # print()

    ans_dict_grouped_list.sort(key=lambda x: (
        x[1]['votes'], x[1]['rank_score']), reverse=True)

    ans_dict_vote_sorted.append({
        'doc_index': doc_index,
        'ans_dict_grouped_list': ans_dict_grouped_list,
    })

    # if int(doc_index) >= 5:
    #     break

# print('what the ans_dict_vote_sorted is:')
# pprint.pprint(ans_dict_vote_sorted)
# print()

ans_dict_vote_sorted.sort(key=lambda x: int(x['doc_index']))

# print('what the ans_dict_vote_sorted is at #2:')
# pprint.pprint(ans_dict_vote_sorted)
# print()

counter_votes_first_g2t = 0
counter_votes_from_both = 0
counter_votes_first_g2t_second_su = 0
# train_eda6_op4_robert_newpost 和 train_eda3_op4_robert_newpost
# counter_special_two = 0

for i, ans_dict_voted in enumerate(ans_dict_vote_sorted):

    # if votes_all_from_filter(ans_dict_voted['ans_dict_grouped_list'][0][1]['votes_source']):
    #     counter_votes_first_g2t += 1
    #     print('doc_index: ', ans_dict_voted['doc_index'])
    #     pprint.pprint(ans_dict_voted)
    #     print()

    # votes_special_two_filtered = list(filter(lambda x: is_legal_ans(x[0]) and (len(x[1]['votes_source']) == 2) and ('train_eda6_op4_robert_newpost' in x[1]['votes_source']) and (
    #     'train_eda3_op4_robert_newpost' in x[1]['votes_source']), ans_dict_voted['ans_dict_grouped_list']))

    # if len(votes_special_two_filtered) == 1:
    #     counter_special_two += 1

    #     print('doc_index BEFORE: ', ans_dict_voted['doc_index'])
    #     pprint.pprint(ans_dict_voted)
    #     print()

    #     ans_dict_vote_sorted[i]['ans_dict_grouped_list'] = votes_special_two_filtered

    #     print('doc_index AFTER: ', ans_dict_voted['doc_index'])
    #     pprint.pprint(ans_dict_voted)
    #     print()

    # else:

    votes_extreme_list_filtered = list(filter(lambda x: is_legal_ans(x[0]) and (not votes_all_from_filter(x[1]['votes_source'], votes_thresh=1)) and (not votes_all_from_filter(
        x[1]['votes_source'], filter_='train_', votes_thresh=1)), ans_dict_voted['ans_dict_grouped_list']))

    if len(votes_extreme_list_filtered) > 0:
        counter_votes_from_both += 1
        votes_extreme_list_filtered.sort(
            key=lambda x: x[1]['votes'], reverse=True)

        # print('doc_index BEFORE: ', ans_dict_voted['doc_index'])
        # pprint.pprint(ans_dict_voted)
        # print()

        ans_dict_vote_sorted[i]['ans_dict_grouped_list'] = votes_extreme_list_filtered

        # print('doc_index: ', ans_dict_voted['doc_index'])
        # pprint.pprint(votes_extreme_list_filtered)
        # print()

        # print('doc_index AFTER: ', ans_dict_voted['doc_index'])
        # pprint.pprint(ans_dict_voted)
        # print()

    elif votes_all_from_filter(ans_dict_voted['ans_dict_grouped_list'][0][1]['votes_source'], votes_thresh=3) \
            and (len(ans_dict_voted['ans_dict_grouped_list']) > 1) \
            and (votes_all_from_filter(ans_dict_voted['ans_dict_grouped_list'][1][1]['votes_source'], filter_='train_', votes_thresh=1)) \
            and is_legal_ans(ans_dict_voted['ans_dict_grouped_list'][1][0]):
        counter_votes_first_g2t_second_su += 1

        # print('doc_index BEFORE: ', ans_dict_voted['doc_index'])
        # pprint.pprint(ans_dict_voted)
        # print()

        ans_dict_vote_sorted[i]['ans_dict_grouped_list'] = ans_dict_voted['ans_dict_grouped_list'][1:]

        # print('doc_index AFTER: ', ans_dict_voted['doc_index'])
        # pprint.pprint(ans_dict_voted)
        # print()

# print('what the ans_dict_vote_sorted is at #3:')
# pprint.pprint(ans_dict_vote_sorted)
# print()

print('投票列表中，能够找到投票来源，包含两类模型的：', counter_votes_from_both, '占比：',
      counter_votes_from_both/len(ans_dict_vote_sorted))
print()

# print('得票最多的，均来自g2t：', counter_votes_first_g2t, '占比：',
#       counter_votes_first_g2t/len(ans_dict_vote_sorted))
# print()

# print('如果不是上面的情况，得票数为2，且分别来自特例：train_eda6_op4_robert_newpost和train_eda3_op4_robert_newpost的：', counter_special_two, '占比：',
#       counter_special_two/len(ans_dict_vote_sorted))
# print()

print('如果不是上面的情况，得票最多的，均来自g2t，且得票次多的，均来自seq2seq的：', counter_votes_first_g2t_second_su, '占比：',
      counter_votes_first_g2t_second_su/len(ans_dict_vote_sorted))
print()


# 如果发现已经生成，则删掉
if os.path.exists('../submits/submit_voted_merged.csv'):
    os.system('rm -rf "../submits/submit_voted_merged.csv"')

# 生成的融合后的文件路径，根据实际情况调整
if not os.path.exists('../submits/submit_voted_merged.csv'):
    test_submit_f = open(
        '../submits/submit_voted_merged.csv', 'w', encoding='utf-8')
    csv_writer_submit = csv.writer(test_submit_f)

counter_not_legal_ans = 0
for item in ans_dict_vote_sorted:
    if not is_legal_ans(item['ans_dict_grouped_list'][0][0]):
        counter_not_legal_ans += 1
        print(item['ans_dict_grouped_list'][0][0])
    elif item['ans_dict_grouped_list'][0][0].strip() == '':
        counter_not_legal_ans += 1
        print(item['ans_dict_grouped_list'][0][0])
    csv_writer_submit.writerow(
        [item['doc_index'], item['ans_dict_grouped_list'][0][0]])

print('最终的不合法答案数：', counter_not_legal_ans, '占比：',
      counter_not_legal_ans/len(ans_dict_vote_sorted))
print()
