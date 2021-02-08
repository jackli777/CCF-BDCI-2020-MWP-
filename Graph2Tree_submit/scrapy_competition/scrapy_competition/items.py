# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyTutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ZybangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    question_searched = scrapy.Field()
    fraction_nums_question = scrapy.Field()
    calculation_procedures = scrapy.Field()
    fraction_nums_cal = scrapy.Field()
    is_best_ans = scrapy.Field()
    doc_index = scrapy.Field()
    des = scrapy.Field()
    lcs = scrapy.Field()
    lcs_satisfied = scrapy.Field()
    origin = scrapy.Field()
    time = scrapy.Field()
    title = scrapy.Field()
    title_question = scrapy.Field()
    type_ = scrapy.Field()
    url = scrapy.Field()
    url_real = scrapy.Field()
