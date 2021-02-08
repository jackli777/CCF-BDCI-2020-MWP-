import copy
import pickle
import pprint

import scrapy
from scrapy_competition.items import ZybangItem
from tqdm import tqdm

searched_results_path = '../competition/generated/search_scraper_processed/train_searched_results.pkl'

searched_results = pickle.load(open(searched_results_path, 'rb'))

# print('what the last 10 items of searched_results are:')
# pprint.pprint(searched_results[-10:])
# print('and its original length is:')
# pprint.pprint(len(searched_results))
# print()


searched_results_zybang = list(map(lambda x: list(
    filter(lambda y: y['site_name'] == 'zybang_com', x)), searched_results))

# print('what the last 10 items of searched_results_zybang are:')
# pprint.pprint(searched_results_zybang[-10:])
# print('and its original length is:')
# pprint.pprint(len(searched_results_zybang))
# print()


# 对于没有url_real的，还是给个假的问题，但是能够在 作业帮 上找到的，但没有在train中的
# 占位问题：对数的概念
question_placeholder_zybang = 'https://www.zybang.com/question/4eed7bdadb78772b12fe211dfb0e3f0c.html'

dict_placeholder_zybang = {
    'des': '占位问题',
    'doc_index': -7,
    'origin': '作业帮',
    'time': None,
    'title': '占位问题',
    'title_question': '占位问题，根据doc_index，去比赛数据中查实际的问题文本',
    'type': 'result',
    'url': 'http://www.placeholder.com',
    'url_real': question_placeholder_zybang,
}


start_urls_dict_list_zybang = []
for i, searched_result in enumerate(searched_results_zybang):
    if len(searched_result) > 0:

        dict_to_append_list = []
        for j, _ in enumerate(searched_result):
            # 后面加上GET参数，response.url的时候可以拿到doc_index
            searched_result[j]['results_content']['url_real'] = searched_result[j]['results_content']['url_real'] + \
                f"?doc_index={searched_result[j]['results_content']['doc_index']}"
            dict_to_append_list.append(searched_result[j]['results_content'])

    else:
        dict_to_append = copy.deepcopy(dict_placeholder_zybang)
        dict_to_append['doc_index'] = i
        # 后面加上GET参数，response.url的时候可以拿到doc_index
        dict_to_append['url_real'] = dict_to_append['url_real'] + \
            f"?doc_index={dict_to_append['doc_index']}"
        dict_to_append_list = [dict_to_append]
    start_urls_dict_list_zybang.extend(dict_to_append_list)

print('what the last 10 items of start_urls_dict_list_zybang are:')
pprint.pprint(start_urls_dict_list_zybang[-10:])
print('and its original length is:')
pprint.pprint(len(start_urls_dict_list_zybang))
print()

start_urls_dict_zybang = dict()

for dict_ in start_urls_dict_list_zybang:
    start_urls_dict_zybang[dict_['url_real']] = dict_['doc_index']

print('what the last 10 items of start_urls_dict_zybang are:')
pprint.pprint(list(start_urls_dict_zybang.items())[-10:])
print('and its original length is:')
pprint.pprint(len(start_urls_dict_zybang))
print('and the length of unique keys are:')
pprint.pprint(len(set(start_urls_dict_zybang.keys())))
print()


class ZybangSpider(scrapy.Spider):
    name = "zybang"
    allowed_domains = ["zybang.com"]
    start_urls = tqdm(list(start_urls_dict_zybang.keys()))

    def parse(self, response):

        for sel in response.css('body > div.layout.main-body'):

            item = ZybangItem()

            # body > div.layout.main-body > div.main-con > div.questionWarp > dl > dd > span
            item['question_searched'] = sel.css(
                'div.main-con > div.questionWarp > dl > dd > span').extract()
            item['fraction_nums_question'] = sel.css(
                'div.main-con > div.questionWarp > dl > dd > span .MathZyb').extract()

            # #good-answer > dd > span
            item['calculation_procedures'] = sel.xpath(
                '//*[@id="good-answer"]/dd/span').extract()
            item['fraction_nums_cal'] = sel.xpath(
                '//*[@id="good-answer"]/dd/span').css('.MathZyb').extract()

            is_best_ans = True
            if len(item['calculation_procedures']) == 0:
                # body > div.layout.main-body > div.main-con > dl > dd > span
                item['calculation_procedures'] = sel.css(
                    'div.main-con > dl > dd > span').extract()
                # body > div.layout.main-body > div.main-con > dl > dd > span .MathZyb 如果有分数的话
                item['fraction_nums_cal'] = sel.css(
                    'div.main-con > dl > dd > span .MathZyb').extract()
                is_best_ans = False

            item['is_best_ans'] = is_best_ans

            # 此处response.url的GET参数中已经包含了doc_index，unique的会更多
            item['doc_index'] = start_urls_dict_zybang[response.url]

            # 此处两个条件都要满足，url_real和doc_index
            matched_zybang_dict_list = list(filter(
                lambda x: (x['url_real'] == response.url) and (x['doc_index'] == item['doc_index']), start_urls_dict_list_zybang))

            if len(matched_zybang_dict_list) > 0:
                matched_zybang_dict = matched_zybang_dict_list[0]
            else:
                matched_zybang_dict = copy.deepcopy(dict_placeholder_zybang)
                matched_zybang_dict['doc_index'] = item['doc_index']

            item['des'] = matched_zybang_dict['des']
            item['origin'] = matched_zybang_dict['origin']
            item['time'] = matched_zybang_dict['time']
            item['title'] = matched_zybang_dict['title']
            item['title_question'] = matched_zybang_dict['title_question']
            item['type_'] = matched_zybang_dict['type']
            item['url'] = matched_zybang_dict['url']
            item['url_real'] = matched_zybang_dict['url_real']

            yield item
