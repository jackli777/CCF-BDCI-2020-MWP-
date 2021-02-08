import copy
import csv
import os
import pickle
import platform
import pprint

import requests
# 导入BaiduSpider
from baiduspider import BaiduSpider
from tqdm import tqdm, trange

# from data_process_timeout import null_callback, time_out
from data_process_utils import (char_unify_convertor, convert_cn_colon_to_en,
                                convert_en_punct_to_cn, del_spaces,
                                replace_1_with_l, replace_l_with_1,
                                rm_pinyin_yinjie)

# 实例化BaiduSpider
spider = BaiduSpider()


# 填入比赛数据的train
target_file_name = 'train'
file_to_write = f'{target_file_name}_searched_results.pkl'

# 路径根据实际情况调整
target_file = f'../official_data/{target_file_name}.csv'

search_scraper_memo_path = f'search_scraper_memo_{target_file_name}.pkl'


# 多个站点搜索，均记录，分别统计
# 实际上发现：mofangge爬取速度过慢，有时间的话可以做；百度知道上的答案格式不统一，后续提取表达式和答案较为困难
search_site_lists = [
    'zybang.com',
    # 'mofangge.com',
    # 'zhidao.baidu.com',
]

# 对于没有url_real的，还是给个假的问题，但是能够在 作业帮 上找到的，但没有在train中的
# 占位问题：对数的概念
question_placeholder_zybang = 'https://www.zybang.com/question/4eed7bdadb78772b12fe211dfb0e3f0c.html'
# question_placeholder_baidu_zhidao = 'https://zhidao.baidu.com/question/1501982592157644739.html'
# question_placeholder_mofangge = 'https://www.mofangge.com/html/qDetail/02/g0/201401/ua8sg002434659.html'

dict_placeholder_zybang = {
    'des': '占位问题',
    # 此处初始值，将会由待搜索的问题索引进行覆盖
    'doc_index': -7,
    'origin': '作业帮',
    'time': None,
    'title': '占位问题',
    'title_question': '占位问题，根据doc_index，去比赛数据中查实际的问题文本',
    'type': 'result',
    'url': 'http://www.placeholder.com',
    'url_real': question_placeholder_zybang,
}

# dict_placeholder_baidu_zhidao = {
#     'des': '占位问题',
#     'doc_index': -7,
#     'origin': '百度知道',
#     'time': None,
#     'title': '占位问题',
#     'title_question': '占位问题，根据doc_index，去比赛数据中查实际的问题文本',
#     'type': 'result',
#     'url': 'http://www.placeholder.com',
#     'url_real': question_placeholder_baidu_zhidao,
# }

# dict_placeholder_mofangge = {
#     'des': '占位问题',
#     'doc_index': -7,
#     'origin': '魔方格',
#     'time': None,
#     'title': '占位问题',
#     'title_question': '占位问题，根据doc_index，去比赛数据中查实际的问题文本',
#     'type': 'result',
#     'url': 'http://www.placeholder.com',
#     'url_real': question_placeholder_mofangge,
# }


def get_query_result(query):
    try:
        query_result = spider.search_web(query=query)
    except:
        query_result = None
    return query_result


if os.path.exists(file_to_write):
    searched_results = pickle.load(open(file_to_write, 'rb'))
    search_scraper_memo = pickle.load(open(search_scraper_memo_path, 'rb'))
    doc_index_processed = search_scraper_memo['doc_index_processed']
    print('searched_results loaded before entering the iteration, now its length is: ', len(
        searched_results))
    print('search_scraper_memo loaded before entering the iteration, now the doc_index_processed is: ', doc_index_processed)
    print()
else:
    searched_results = []
    doc_index_processed = -1

with open(target_file, 'r') as f:
    reader = csv.reader(f)
    for doc_index, row in enumerate(tqdm(reader)):

        if doc_index <= doc_index_processed:
            continue

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

        # 将表示比例的中文冒号转为英文冒号
        question = convert_cn_colon_to_en(question)

        # 将英文标点转为中文
        # question = convert_en_punct_to_cn(question)

        query_list = []
        for site in search_site_lists:
            site_name = site.replace('.', '_')
            query_list.append({
                'site_name': site_name,
                'query': f'''site:{site} "{question}"'''
            })

        # pprint.pprint(query_list)
        # print()

        query_result_list = []
        for q in query_list:

            query_result = get_query_result(q['query'])

            query_result_list.append({
                'site_name': q['site_name'],
                'query_result': query_result,
            })

        # pprint.pprint(query_result_list)
        # print()

        results_content_list = []
        for q in query_result_list:
            if (q['query_result'] is not None) and (len(q['query_result']['results']) > 0):
                results_content = q['query_result']['results']
                results_content = list(filter(lambda x: ('des' in x.keys()) and (
                    'title' in x.keys()), results_content))

                for i, _ in enumerate(results_content[:10]):
                    results_content[i]['doc_index'] = doc_index
                    results_content[i]['url_real'] = requests.get(
                        results_content[i]['url'].strip()).url
                    results_content[i]['title_question'] = question

                    results_content_list.append({
                        'site_name': q['site_name'],
                        'results_content': results_content[i]
                    })

            else:
                if q['site_name'] == 'zybang_com':
                    results_content_dict = copy.deepcopy(
                        dict_placeholder_zybang)
                # elif q['site_name'] == 'zhidao_baidu_com':
                #     results_content_dict = copy.deepcopy(
                #         dict_placeholder_baidu_zhidao)
                # elif q['site_name'] == 'mofangge_com':
                #     results_content_dict = copy.deepcopy(
                #         dict_placeholder_mofangge)

                results_content_dict['doc_index'] = doc_index

                results_content_list.append({
                    'site_name': q['site_name'],
                    'results_content': results_content_dict,
                })

        # pprint.pprint(results_content_list)
        # print()

        searched_results.append(results_content_list)

        if (doc_index != 0) and (doc_index % 100 == 0):
            os.system(f'rm -rf "{file_to_write}"')
            pickle.dump(searched_results, open(f'{file_to_write}', 'wb'))
            os.system(f'rm -rf "{search_scraper_memo_path}"')
            pickle.dump({'doc_index_processed': doc_index},
                        open(f'{search_scraper_memo_path}', 'wb'))
            print(
                f'searched_results dumped for doc_index {doc_index}, now its length is {len(searched_results)}')
            print(f'search scraper memo dumped for doc_index {doc_index}')
            print()

        # break
        # if doc_index > 200:
        #     break

# 已处理完，再加载一次：
if 'doc_index' not in dir():
    doc_index = doc_index_processed

# 循环结束的时候再保存一次
os.system(f'rm -rf "{file_to_write}"')
pickle.dump(searched_results, open(f'{file_to_write}', 'wb'))
os.system(f'rm -rf "{search_scraper_memo_path}"')
pickle.dump({'doc_index_processed': doc_index},
            open(f'{search_scraper_memo_path}', 'wb'))
print(
    f'searched_results dumped after the iteration, now the doc_index is {doc_index}, now its length is {len(searched_results)}')
print(
    f'search scraper memo dumped after the iteration, now the doc_index is {doc_index}')
print()

print('what the last 10 items of searched_results are:')
pprint.pprint(searched_results[-10:])
print('and its original length is:')
pprint.pprint(len(searched_results))
print()
