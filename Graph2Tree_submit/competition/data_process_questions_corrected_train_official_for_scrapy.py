import csv
import json
import os
import pprint

file_name = 'items_zybang_train_processed.json'
file_corrected_name = 'items_zybang_train_processed_corrected.json'

scrapy_results_path = f'./generated/scrapy_processed/{file_name}'

scrapy_results = json.load(open(scrapy_results_path, 'r'))
scrapy_results.sort(key=lambda x: x['doc_index'])

print('what the first 10 items of scrapy_results are:')
pprint.pprint(scrapy_results[:10])
print('and its length is:')
pprint.pprint(len(scrapy_results))
print()


def process_questions_corrected(scrapy_results, doc_index, correct_ans=-1000, correct_equation='x=1+2', des='train文件中题目错误修订', correct_question=''):
    scrapy_results[doc_index]['ans_crawled'] = f'{correct_ans}'
    scrapy_results[doc_index]['calculation_procedures'] = []
    scrapy_results[doc_index]['calculation_procedures_cleaned_list'] = []
    scrapy_results[doc_index]['des'] = des
    scrapy_results[doc_index]['doc_index'] = doc_index
    scrapy_results[doc_index]['equation_crawled'] = correct_equation
    scrapy_results[doc_index]['fraction_nums_cal'] = []
    scrapy_results[doc_index]['fraction_nums_question'] = []
    scrapy_results[doc_index]['is_best_ans'] = 1
    scrapy_results[doc_index]['lcs'] = ''
    scrapy_results[doc_index]['lcs_len'] = 0
    scrapy_results[doc_index]['origin'] = '手动处理'
    scrapy_results[doc_index]['question_searched'] = []
    scrapy_results[doc_index]['question_searched_cleaned_list'] = []
    scrapy_results[doc_index]['time'] = None
    scrapy_results[doc_index]['title'] = ''
    scrapy_results[doc_index]['title_question'] = correct_question
    scrapy_results[doc_index]['type_'] = ''
    scrapy_results[doc_index]['url'] = ''
    scrapy_results[doc_index]['url_real'] = ''


for i, item in enumerate(scrapy_results):
    if item['doc_index'] == 1226:

        # print('what the item if before:')
        # pprint.pprint(item)
        # print()

        # http://www.1010jiajiao.com/xxsx/shiti_id_c5c4cb6582a7d24a0209e679ee436d67
        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=6,
                                    correct_equation='x=2*3',
                                    des='train文件中题目错误修订，备注：该题求最大公约数的，无法用一步算式表达',
                                    correct_question='一个长方形的池塘，长为54米，宽为42米。如果在它的四周及四角栽上风景树，每相邻两棵树之间的距离要相等，那么最多每几米栽一棵？'
                                    )

        # print('and what is after:')
        # pprint.pprint(scrapy_results[1226])
        # print()

    elif item['doc_index'] == 1593:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=460,
                                    correct_equation='x=115*4',
                                    des='train文件中题目错误修订',
                                    correct_question='购买体育用具．学校买了4副围棋，一副围棋115元，需要多少钱？'
                                    )

    elif item['doc_index'] == 1596:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=4550,
                                    correct_equation='x=(100-65)*130',
                                    des='train文件中题目错误修订',
                                    correct_question='商场从厂家批发了130个排球，每个排球进价65元．售价为100元，这些排球售完后能赚多少钱？'
                                    )

    elif item['doc_index'] == 1953:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=71,
                                    correct_equation='x=171-44-56',
                                    des='train文件中题目错误修订',
                                    correct_question='安岳距成都171千米，一辆客车从安岳出发，第1小时行了44千米，第2小时行了56千米，行驶了2小时后还要行驶多少千米才能到达成都？'
                                    )

    elif item['doc_index'] == 3526:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='1/4',
                                    correct_equation='x=3/4+1/2-1',
                                    des='train文件中题目错误修订，备注：感觉答案还是错的，正确答案应该是1/4，给的答案是4/5',
                                    correct_question='儿童用品商场计划六月一日全天的销售额为1万元，实际上午销售3/4万元，下午销售1/2万元，全天超额多少万元？'
                                    )

    elif item['doc_index'] == 3622:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=48,
                                    correct_equation='x=6*8',
                                    des='train文件中题目错误修订，备注：是求最小公倍数的，但这题恰好是两个数的乘积',
                                    correct_question='五(1)班有四十多名学生，上体育课玩分组游戏。6人一组恰好分完，8人一组也恰好分完。这个班有多少名同学？'
                                    )

    elif item['doc_index'] == 5220:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=10,
                                    correct_equation='x=600-(356+234)',
                                    des='train文件中题目错误修订',
                                    correct_question='妈妈买了一件衣服用了356元，又买了一条裤子用了234元．妈妈付给营业员600元，应该找回多少元？'
                                    )

    elif item['doc_index'] == 5589:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=12,
                                    correct_equation='x=36/(12-9)',
                                    des='train文件中题目错误修订',
                                    correct_question='聪聪和明明玩取围棋子的游戏，聪聪每次取12枚黑子，明明每次取9枚白子，取了几次后，黑子没有了,白子还有36枚，黑子和白子同样多，问取了几次？'
                                    )

    elif item['doc_index'] == 5063:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=36,
                                    correct_equation='x=9+9*3',
                                    des='train文件中题目错误修订',
                                    correct_question='青蛙弟弟捉了9只害虫，青蛙哥哥捉的害虫只数是青蛙弟弟的3倍．他们一共捉了多少只害虫？'
                                    )

    elif item['doc_index'] == 5945:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=168,
                                    correct_equation='x=12*14',
                                    des='train文件中题目错误修订',
                                    correct_question='2011年7月1日建党九十周年纪念日，为纪念这一隆重的节日，中国邮政发行了纪念建党九十周年明信片。每套12张，售价14元。一套明信片多少钱？'
                                    )

    elif item['doc_index'] == 8251:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='1/6',
                                    correct_equation='x=40/60-1/5-3/10',
                                    des='train文件中题目错误修订',
                                    correct_question='一堂40分钟的数学课上，学生动手操作用了1/5小时，老师讲课用了3/10小时，其余的时间学生独立做作业，学生独立做作业用了多少时间？'
                                    )

    elif item['doc_index'] == 9502:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=576,
                                    correct_equation='x=8*6*12',
                                    des='train文件中题目错误修订',
                                    correct_question='每人每天装8台电脑，他们6人12天能装多少台？'
                                    )

    elif item['doc_index'] == 9591:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=7,
                                    correct_equation='x=450/62',
                                    des='train文件中题目错误修订，备注：这题是向下取整的',
                                    correct_question='一个篮球62元，450元可以买几个？'
                                    )

    elif item['doc_index'] == 10692:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=104,
                                    correct_equation='x=2000*3.25%*2*(1-20%)',
                                    des='train文件中题目错误修订',
                                    correct_question='萍萍将2000元压岁钱存入银行，年利率按3.25%计算，准备在二年后将利息捐给“希望工程”。如果利息税为20%，到期后她能捐多少钱？'
                                    )

    elif item['doc_index'] == 10228:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=5,
                                    correct_equation='x=19/4',
                                    des='train文件中题目错误修订，备注：这题是向上取整的',
                                    correct_question='星期六三年级二班的19个同学去儿童公园划船，每条船限乘4人。他们至少要租几条船？'
                                    )

    elif item['doc_index'] == 10263:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=240,
                                    correct_equation='x=420*4/7',
                                    des='train文件中题目错误修订',
                                    correct_question='花生仁的营养价值很高，一般每千克花生仁可榨油4/7千克，420千克花生仁可榨油多少千克？'
                                    )

    elif item['doc_index'] == 10265:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=24,
                                    correct_equation='x=6/7/(2/7-1/4)',
                                    des='train文件中题目错误修订',
                                    correct_question='某工程队修一条路，第一周修了这段公路的1/4，第二周修了这条路的2/7，第二周比第一周多修了6/7千米。这段公路全长多少米？'
                                    )

    elif item['doc_index'] == 10270:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='1.2',
                                    correct_equation='x=14/5*3/7',
                                    des='train文件中题目错误修订，备注：表达式中的算式都是分数，但结果是小数',
                                    correct_question='制造一台机器，原来用钢材2_4/5吨。现在用的比原来节约3/7，现在一台机器节约钢材多少吨？'
                                    )

    elif item['doc_index'] == 10289:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='9/2',
                                    correct_equation='x=3/4*6',
                                    des='train文件中题目错误修订',
                                    correct_question='重阳节快到了，小英想和同学们一起做几个中国结送给福利院的爷爷奶奶。做一个要用3/4米彩绳，小英想做6个，至少要准备多少米彩绳？'
                                    )

    elif item['doc_index'] == 10337:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='42%',
                                    correct_equation='x=42/100',
                                    des='train文件中题目错误修订',
                                    correct_question='100千克花生可以榨油42千克求出油率。'
                                    )

    elif item['doc_index'] == 10346:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='42%',
                                    correct_equation='x=42/100',
                                    des='train文件中题目错误修订',
                                    correct_question='100千克花生可以榨油42千克求出油率。'
                                    )

    # 以下是“train文件中答案修订错误”，但实际上题目也修订了的（类型3），且题目中的数值，或是数值后的单位有实质变化的（类型2），应该加入到“train文件中题目修订错误”中：
    elif item['doc_index'] == 590:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='3/2',
                                    correct_equation='x=2*3/4',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='一个长方形长2米,宽3/4米，它的面积是多少平方米？'
                                    )

    elif item['doc_index'] == 664:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='37.68',
                                    correct_equation='x=3.14*(4/2)^2+3.14*4*2',
                                    des='train文件中题目错误修订，备注：类型3',
                                    correct_question='要砌一个圆柱形的沼气池，底面直径是4米，深2米。在池的周围与底面抹上水泥，抹水泥部分的面积是多少平方米？'
                                    )

    elif item['doc_index'] == 705:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='2_1/5',
                                    correct_equation='x=3-2/5*2',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='甲桶有油3千克，从甲桶取出2/5千克，倒入乙桶，这时两桶油一样重，乙桶原有油多少千克？'
                                    )

    elif item['doc_index'] == 3558:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='25/9',
                                    correct_equation='x=50/3/6',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='一袋大米重50/3千克，平均分给6个人。每个人分得多少千克？'
                                    )

    elif item['doc_index'] == 6886:
        # TODO 使用原来的答案
        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=588,
                                    correct_equation='x=21*28',
                                    des='train文件中题目错误修订，备注：类型3，正确答案给的是600，但还是按588算，否则后续提取表达式的时候会被过滤掉',
                                    correct_question='一本书一页有21行，每行28个字。估计一下，这一页大约有多少个字？'
                                    )

    elif item['doc_index'] == 6887:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=605,
                                    correct_equation='x=125*4-20+125',
                                    des='train文件中题目错误修订，备注：类型3',
                                    correct_question='一个果园里栽了125棵苹果树，梨树的棵数比苹果树的4倍少20棵。这个果园一共栽了多少棵树？'
                                    )

    elif item['doc_index'] == 7046:
        # https://wenku.baidu.com/view/fa6c36d6aaea998fcd220ea1.html
        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='320.76',
                                    correct_equation='x=(24*10+24*3*2+10*3*2-120)*0.5*(1+1-1/5)*(1+10%)',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='逸夫希望小学多媒体教室的长是24米，宽10米，高3米，现决定趁暑假给天花板和四周的墙壁重新粉刷,已知门窗的面积占120平方米。若第一遍每平方米需用涂料0.5升,第二遍粉刷时比第一遍节约1/5，实际粉刷时还有10%的损耗率。请你帮助计算一下，共需购买涂料多少升？'
                                    )

    elif item['doc_index'] == 7787:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='25%',
                                    correct_equation='x=(1/(10-2)-1/10)/(1/10)',
                                    des='train文件中题目错误修订，备注：类型3',
                                    correct_question='一件工程计划10天完成，实际提前2天完成任务，实际比计划的工作效率提高了多少．'
                                    )

    elif item['doc_index'] == 8573:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=3250,
                                    correct_equation='x=30*25*5-4*5^3',
                                    des='train文件中题目错误修订，备注：类型3',
                                    correct_question='一个长方体铁皮盒子长30cm，宽25cm，高5cm从四个角各切掉一个长为5cm的正方体，剩下的物体的容积是多少？'
                                    )

    elif item['doc_index'] == 8662:
        # TODO 使用原来的答案
        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=48,
                                    correct_equation='x=8/(1.4-1)*(1+1.4)',
                                    des='train文件中题目错误修订，备注：类型3，这道题是两问，还是按照原来一问的处理',
                                    correct_question='两袋白砂糖，甲袋的重量是乙袋的1.4倍，如果乙袋增加8千克，两袋糖就一样重，原来每袋糖共多少千克'
                                    )

    elif item['doc_index'] == 8829:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=50,
                                    correct_equation='x=225/2.5*5/(4+5)',
                                    des='train文件中题目错误修订，备注：类型3',
                                    correct_question='两个城市相距225千米，一辆客车和一辆货车同时从这两城市相对开出，2.5小时后相遇，货车与客车速度比是4:5，客车每小时行多少千米'
                                    )

    elif item['doc_index'] == 9280:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=140,
                                    correct_equation='x=28*5',
                                    des='train文件中题目错误修订，备注：类型2，数值后的单位名称变化',
                                    correct_question='水果店运来5车水果，每车装28千克，水果店运来水果一共多少千克？'
                                    )

    elif item['doc_index'] == 10352:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='4/33',
                                    correct_equation='x=24/33/6',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='一块6公顷的菜地需施肥24/33吨，平均每公顷施肥多少吨？'
                                    )

    elif item['doc_index'] == 10484:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='3/4',
                                    correct_equation='x=1/20*15',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='小明每分钟步行1/20千米。照这样计算，他15分钟可步行多少千米？'
                                    )

    elif item['doc_index'] == 10541:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='2/5',
                                    correct_equation='x=3/4*(8/(8+7))',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='学校食堂九月份和十月份用煤量的比是8:7，两个月共用煤3/4吨。九月用煤多少吨？'
                                    )

    elif item['doc_index'] == 10670:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='3/5',
                                    correct_equation='x=3/20*4',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='一台电视机每小时耗电3/20千瓦时，张奶奶家平均每天收看4小时，她家电视机平均每天耗电多少千瓦时？'
                                    )

    elif item['doc_index'] == 10794:
        # TODO 使用这里的问题
        # https://zhidao.baidu.com/question/424959142.html
        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=4500,
                                    correct_equation='x=300*15',
                                    des='train文件中题目错误修订，备注：类型3，题目少一问，给的答案是第二问的，第一问正确答案是80*15=1200',
                                    correct_question='小华带着自己的爱犬去姥姥家，已知小华步行的速度是每分钟80米，犬的速度每分钟300米。她和犬同时从家里出发，犬跑到姥姥家后马上调头找小华，和小华相遇后又马上调头跑向姥姥家，就这样犬来回的跑。小华到姥姥家共用时15分钟，由此可知小华家离姥姥家多少米，犬跑了多少米？'
                                    )

    elif item['doc_index'] == 10838:
        # TODO 使用这里的答案
        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans='87/23',
                                    correct_equation='x=(506-158)/(52+40)',
                                    des='train文件中题目错误修订，备注：类型2，答案给了两问的，但问题只有一问',
                                    correct_question='甲乙两车同时从相距506千米的两地相向开出，甲车每小时行52千米，乙车每小时行40千米，那么几小时后两车相距158千米？'
                                    )

    elif item['doc_index'] == 10959:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=63,
                                    correct_equation='x=15*42*100/1000',
                                    des='train文件中题目错误修订，备注：类型2',
                                    correct_question='奶牛场每头奶牛平均日产牛奶15千克，42头奶牛100天可产奶多少吨？'
                                    )

    elif item['doc_index'] == 11456:

        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=32,
                                    correct_equation='x=(12/3+12)*2',
                                    des='train文件中题目错误修订，备注：类型3',
                                    correct_question='把一个边长12厘米的正方形剪成三个完全一样的小长方形，每个小长方形的周长是多少？'
                                    )

    # 有两个答案的作为特例（类型4）再处理下：
    elif item['doc_index'] == 7175:
        # TODO 这题修正后有两个答案，现在处理成一个
        process_questions_corrected(scrapy_results,
                                    item['doc_index'],
                                    correct_ans=4,
                                    correct_equation='x=250/60',
                                    des='train文件中题目错误修订，备注：类型4，向下取整',
                                    correct_question='一把椅子60元，250元最多能买几把椅子？'
                                    )

json.dump(scrapy_results, open(file_corrected_name, 'w'), ensure_ascii=False)
