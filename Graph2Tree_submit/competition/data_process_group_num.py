import csv
import json
import operator
import os
import platform
import pprint
import re

from tqdm import tqdm

from data_process_utils import (char_unify_convertor, convert_cn_colon_to_en,
                                convert_en_punct_to_cn,
                                convert_mixed_num_to_fraction_for_graph2tree,
                                convert_some_mentions, del_spaces,
                                generate_group_num, generate_num_list,
                                num_keys_list, process_add_info,
                                replace_1_with_l, replace_l_with_1,
                                revert_back_to_num, rm_pinyin_yinjie,
                                units_list, units_mention_unify)
from graph_to_tree_utils import TARGET_FILE_GROUP_NUM

# 如果运行的环境是Linux（我的云服务器是Linux的）
if platform.system().lower() == 'linux':
    import hanlp
    from hanlp.common.trie import Trie
    from hanlp.utils.log_util import init_logger


# 如果运行的环境是Linux（我的云服务器是Linux的）
if platform.system().lower() == 'linux':

    # WARNING Input tokens [已分词的str列表] exceed the max sequence length of 128. The exceeded part will be truncated and ignored. You are recommended to split your long text into several sentences within 128 tokens beforehand.
    # 发现其实都处理了，所以不再打印此类warning
    _logger = init_logger(
        name='hanlp', level=os.environ.get('HANLP_LOG_LEVEL', 'FATAL'))

    # 查看下hanlp用于分词的最新模型
    print('tokenizer: ')
    pprint.pprint(dir(hanlp.pretrained.cws))
    print()

    # 查看下hanlp用于词性标注的最新模型
    print('tagger: ')
    pprint.pprint(dir(hanlp.pretrained.pos))
    print()

    # 查看下hanlp用于依存句法分析的最新模型
    print('syntactic_parser: ')
    pprint.pprint(dir(hanlp.pretrained.dep))
    print()

    # 加载hanlp用于以上流水线任务的模型
    # tokenizer = hanlp.load('PKU_NAME_MERGED_SIX_MONTHS_CONVSEG')
    tokenizer = hanlp.load('LARGE_ALBERT_BASE')
    # tagger = hanlp.load(hanlp.pretrained.pos.CTB5_POS_RNN)
    tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ALBERT_BASE)
    syntactic_parser = hanlp.load(hanlp.pretrained.dep.CTB7_BIAFFINE_DEP_ZH)
    # semantic_parser = hanlp.load(
    #     hanlp.pretrained.sdp.SEMEVAL16_TEXT_BIAFFINE_ZH)

    # pipeline = hanlp.pipeline() \
    #     .append(hanlp.utils.rules.split_sentence, output_key='sentences') \
    #     .append(tokenizer, output_key='tokens') \
    #     .append(tagger, output_key='part_of_speech_tags') \
    #     .append(syntactic_parser, input_key=('tokens', 'part_of_speech_tags'), output_key='syntactic_dependencies') \
    #     .append(semantic_parser, input_key=('tokens', 'part_of_speech_tags'), output_key='semantic_dependencies')

    # 添加自定义字典，也就是上面的num_keys_list + units_list
    custrom_dict = {}
    keys_list = num_keys_list + units_list

    keys_list.sort(key=lambda x: len(x), reverse=True)
    for key in keys_list:
        custrom_dict[key] = key

    trie = Trie()
    # trie.update({'自定义词典': 'custom_dict', '聪明人': 'smart'})
    trie.update(custrom_dict)

    def split_sents(text: str, trie: Trie):
        words = trie.parse_longest(text)

        # https://github.com/hankcs/HanLP/blob/master/tests/demo/zh/demo_cws_trie.py
        # 对官方提供的自定义字典的改造，以处理以下问题：
        # “千米/时”应划分为完整的，而不是再划分出“米/时”
        keys_rm_list = []
        for i, key_i in enumerate(words):
            for j, key_j in enumerate(words):
                if (i != j) and (key_i[3] == key_j[3]) and (key_i[2] < key_j[2]):
                    keys_rm_list.append((key_j[2], key_j[3]))
                elif (i != j) and (key_i[3] == key_j[3]) and (key_i[2] > key_j[2]):
                    keys_rm_list.append((key_i[2], key_i[3]))
                elif (i != j) and (key_i[2] == key_j[2]) and (key_i[3] < key_j[3]):
                    keys_rm_list.append((key_i[2], key_i[3]))
                elif (i != j) and (key_i[2] == key_j[2]) and (key_i[3] > key_j[3]):
                    keys_rm_list.append((key_j[2], key_j[3]))

        words = list(filter(lambda x: (x[2], x[3]) not in keys_rm_list, words))

        sents = []
        pre_start = 0
        offsets = []
        for word, value, start, end in words:
            if pre_start != start:
                sents.append(text[pre_start: start])
                offsets.append(pre_start)
            pre_start = end
        if pre_start != len(text):
            sents.append(text[pre_start:])
            offsets.append(pre_start)
        return sents, offsets, words

    # 测试用例
    # text = '李明㊱年㊴月㊶日把㊲元存入银行，定期整存整取㊷年。如果年利率按⑮计算，到㊳年㊴月㊶日取出时，他可以取出本金和税后利息共多少元？(税率㉒)'
    text = '李明㊱千米/小时㊴米/小时㊶日把㊲千米/分存入银行，定期整存整取㊷米/分钟。如果年利率按⑮米/分，到㊳年㊴月㊶日取出时，他可以取出本金和税后利息共多少元？(税率㉒)'

    print('splitted with trie:')
    print(split_sents(text, trie))
    print()

    def merge_parts(parts, offsets, words):
        items = [(i, p) for (i, p) in zip(offsets, parts)]
        items += [(start, [word]) for (word, value, start, end) in words]
        # In case you need the tag, use the following line instead
        # items += [(start, [(word, value)]) for (word, value, start, end) in words]
        return [each for x in sorted(items) for each in x[1]]

    # pipeline_tokenizer = hanlp.pipeline() \
    #     .append(hanlp.utils.rules.split_sentence, output_key='sentences') \
    #     .append(tokenizer, output_key='tokens')

    pipeline_splitter = hanlp.pipeline() \
        .append(split_sents, output_key=('parts', 'offsets', 'words'), trie=trie)
    splitted = pipeline_splitter(text)

    print('splitted:')
    pprint.pprint(splitted)
    print()

    pipeline_tokenizer = pipeline_splitter.append(
        tokenizer, input_key='parts', output_key='tokens')
    tokenized = pipeline_tokenizer(text)

    print('tokenized:')
    pprint.pprint(tokenized)
    print()

    # 后续使用到的管道
    pipeline_merger = pipeline_tokenizer.append(merge_parts, input_key=(
        'tokens', 'offsets', 'words'), output_key='merged')
    merged = pipeline_merger(text)

    print('merged:')
    pprint.pprint(merged)
    print()

    # pipeline


dataset_to_process = 'competition'

if dataset_to_process == 'competition':

    # 用于切换比赛数据的test or train
    target_file_name = TARGET_FILE_GROUP_NUM

    # 处理test数据，一定不需要EDA
    if 'test' in target_file_name:
        use_eda = -1
    else:
        # 实际上并没有改变data_expansion出来的结果，默认还是9个，这是只是取前20个
        # 若是不想使用EDA，此处设置为0或者小于0的数即可
        use_eda = 20

    # 如果运行的环境是Linux（我的云服务器是Linux的），且要使用EDA的话
    if (use_eda > 0) and (platform.system().lower() == 'linux'):
        from textda.data_expansion import data_expansion

    if platform.system().lower() == 'linux':
        if use_eda > 0:
            file_to_write = f'{target_file_name}_processed_eda.json'
        else:
            file_to_write = f'{target_file_name}_processed.json'
        # 如果上次生成了文件，本次则删除重新生成
        if os.path.exists(file_to_write):
            os.system(f'rm -rf "{file_to_write}"')

    # 路径根据实际情况调整
    target_file = f'../official_data/{target_file_name}.csv'

    if 'train' in target_file_name:
        file_name = 'items_zybang_train_processed_corrected.json'
        scrapy_results_path = f'generated/scrapy_processed/{file_name}'

        scrapy_results = json.load(open(scrapy_results_path, 'r'))
        scrapy_results.sort(key=lambda x: x['doc_index'])

        print('what the first 10 items of scrapy_results are:')
        # pprint.pprint(scrapy_results[:10])
        print('and its length is:')
        pprint.pprint(len(scrapy_results))
        print()

    if (use_eda > 0) and (platform.system().lower() == 'linux'):
        # 由于已知训练数据有12000条，假设每条训练数据，均能从“爬”到的结果中成功提取出正确的表达式和答案
        # 这里对于EDA出来的数据，其索引从15000开始计
        doc_index_eda = doc_index_eda_start = 15000

    if 'train' in target_file_name:
        # 初始化一些统计量
        counter_legal_doc = 0

    if 'train' in target_file_name:
        counter_can_find_equation = 0
        counter_can_find_equation_from_crawled = 0

    with open(target_file, 'r') as f:
        reader = csv.reader(f)

        for doc_index, row in enumerate(tqdm(reader)):

            if 'train' in target_file_name:
                equation_crawled_correct = False
                equation = ''

                doc_index_ = row[0]
                ans_gold = row[2]

                # if ';' in ans_gold:
                #     print(f'for doc_index_ {doc_index_}, ans_gold is: {ans_gold}')
                #     print()

                found_cn_char_in_ans_gold = False
                for char in ans_gold:
                    if '\u4e00' <= char <= '\u9fff':
                        found_cn_char_in_ans_gold = True
                        break

                # if found_cn_char_in_ans_gold:
                #     print(f'for doc_index_ {doc_index_}, ans_gold is: {ans_gold}')
                #     print()

                # 如果发现答案中有中文，如：能，够，是，否，可以，等等，直接跳过，不加入训练
                if found_cn_char_in_ans_gold:
                    continue
                else:

                    """
                    # A榜已经处理了所有双答案的问题
                    if ';' in ans_gold:
                        ans_gold_for_eval_1 = ans_gold.split(
                            ';')[0].replace('%', '/100')
                        ans_gold_for_eval_2 = ans_gold.split(
                            ';')[1].replace('%', '/100')
                        ans_gold_for_eval = ''
                    else:
                        ans_gold_for_eval = ans_gold.replace('%', '/100')
                        ans_gold_for_eval_1 = ans_gold_for_eval_2 = ''
                    """

                    # 处理答案中是带分数的
                    if '_' in ans_gold.strip():
                        int_part = ans_gold.strip().split('_')[0]
                        numerator_raw = ans_gold.strip().split('_')[
                            1].split('/')[0]
                        denominator = ans_gold.strip().split('_')[
                            1].split('/')[1]
                        numerator_new = int(int_part) * \
                            int(denominator) + int(numerator_raw)
                        ans_gold_for_eval = f'{numerator_new}/{denominator}'
                    else:
                        ans_gold_for_eval = ans_gold

                    ans_gold_for_eval = ans_gold_for_eval.replace('%', '/100')

                    equation_crawled = list(filter(lambda x: str(x['doc_index']) == str(
                        doc_index_), scrapy_results))[0]['equation_crawled']
                    equation_crawled_for_eval = equation_crawled.replace(
                        '^', '**').replace('x=', '')
                    equation_crawled_for_eval = re.sub(
                        r'([\.\d]+)%', '(\\1/100)', equation_crawled_for_eval)
                    # TODO “爬”到的表达式中其实处理的不够，特别是带分数，data_process_scrapy_results_zybang.py中也没有怎么处理“爬”到的表达式
                    # 处理特例：3.14*(20/2)2-3.14*62
                    equation_crawled_for_eval = re.sub(
                        r'\((\d+/\d+)\)(\d+)', '((\\1)*\\2)', equation_crawled_for_eval)

                    # A榜已经处理了所有双答案的问题
                    # if ans_gold_for_eval != '':

                    if equation_crawled_for_eval != '':

                        try:
                            eval_diff = eval(
                                equation_crawled_for_eval) - eval(ans_gold_for_eval)

                            abs_diff = abs(eval_diff)
                        except:
                            eval_diff = abs_diff = 1000
                            equation_crawled_correct = False

                        if (abs_diff <= 0.01) or (('.' not in ans_gold_for_eval) and ('/' not in ans_gold_for_eval) and ('%' not in ans_gold_for_eval) and (abs_diff <= 1)):
                            # print(
                            #     f'for doc_index_ {doc_index_}, equation_crawled_for_eval is: {equation_crawled_for_eval}, ans_gold is: {ans_gold}')
                            # print()
                            counter_can_find_equation_from_crawled += 1
                            equation_crawled_correct = True
                        else:
                            equation_crawled_correct = False
                    else:
                        equation_crawled_correct = False

                    equation = ''
                    if equation_crawled_correct:
                        equation = equation_crawled
                    else:
                        equation = ''

                    if equation != '':
                        counter_can_find_equation += 1
                    else:
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

            # 改用封装后的函数，带分数化为假分数（graph2tree用）
            question = convert_mixed_num_to_fraction_for_graph2tree(question)

            # 改用封装后的函数，删除拼音音节
            question = rm_pinyin_yinjie(question)

            # 改用封装后的函数，单位表述进行统一
            question = units_mention_unify(question)

            # 改用封装后的函数，超过1个字符的表述替换
            question = convert_some_mentions(question)

            # 将表示比例的中文冒号转为英文冒号
            question = convert_cn_colon_to_en(question)

            # 带分数化为假分数（graph2tree用）
            question = convert_mixed_num_to_fraction_for_graph2tree(question)

            # 将英文标点转为中文
            question = convert_en_punct_to_cn(question)

            # 改用封装后的函数，处理额外信息，并只附加有意义的额外信息
            question_cleaned = question = process_add_info(question)
            # print(question)

            # 生成该问题的num_list
            generated_num_dict = generate_num_list(question)
            # 该问题文本中的num_list
            num_list = generated_num_dict['num_list']
            # print(num_list)
            # 将所有num替换成字符后的question
            question = generated_num_dict['question_num_replaced']

            if (use_eda > 0) and (platform.system().lower() == 'linux'):
                question_eda_list = data_expansion(
                    question_cleaned, alpha_ri=0)
                for index_, question_cleaned_eda in enumerate(question_eda_list):

                    # 生成该问题的num_list
                    generated_num_dict_eda = generate_num_list(
                        question_cleaned_eda)
                    # 该问题文本中的num_list
                    num_list_eda = generated_num_dict_eda['num_list']
                    # 将所有num替换成字符后的question
                    question_eda = generated_num_dict_eda['question_num_replaced']
                    # TODO 上面提到共用一个num_list，当时只是简单处理了，因为数据增强之后，词序（包括问题文本中出现的数字）可能会发生变化，所以代码中不应简单地使用operator.eq()判断原始问题文本中的num_list和数据增强之后提取的num_list是否相等，而应该先对待判断的两个num_list进行统一规则排序，之后再判断是否相等，这样可以保留更多词序变化带来的可能，也就是能增强出更多合法、且更有变化的问题文本。
                    if operator.eq(num_list_eda, num_list) and (question_cleaned_eda != question_cleaned):
                        question_eda_list[index_] = {
                            'doc_index_originality': doc_index_,
                            'question_cleaned': question_cleaned_eda,
                            'generated_num_dict': generated_num_dict_eda,
                            'num_list': num_list_eda,
                            'question': question_eda,
                        }
                    else:
                        question_eda_list[index_] = {}

                question_eda_list = list(
                    filter(lambda x: len(x) > 0, question_eda_list))
                question_eda_list.sort(key=lambda x: len(x), reverse=True)
                question_eda_list = question_eda_list[:use_eda]

                for index_, _ in enumerate(question_eda_list):
                    doc_index_eda += 1
                    question_eda_list[index_]['doc_index_'] = doc_index_eda

                # print(
                #     f'doc_index: {doc_index}, original cleaned question is:')
                # pprint.pprint(question_cleaned)
                # print('question_eda_list is:')
                # pprint.pprint(question_eda_list)
                # print()

                question_eda_list_ext = [{
                    'doc_index_': doc_index_,
                    'doc_index_originality': 'original',
                    'question_cleaned': question_cleaned,
                    'generated_num_dict': generated_num_dict,
                    'num_list': num_list,
                    'question': question,
                }] + question_eda_list

                # print(
                #     f'doc_index: {doc_index}, original cleaned question is:')
                # pprint.pprint(question_cleaned)
                # print('question_eda_list_ext is:')
                # pprint.pprint(question_eda_list_ext)
                # print()

            if 'train' in target_file_name:
                counter_legal_doc += 1

            if platform.system().lower() == 'linux':

                if use_eda > 0:
                    for stuff in question_eda_list_ext:
                        doc_index_ = stuff['doc_index_']
                        doc_index_originality = stuff['doc_index_originality']
                        generated_num_dict = stuff['generated_num_dict']
                        num_list = stuff['num_list']
                        question = stuff['question']
                        question_cleaned = stuff['question_cleaned']

                        # 使用hanlp进行分词，此时question中的数字均替换为字符
                        hanlp_segmented_text_list = pipeline_merger(question)[
                            'merged']

                        # 分完词后再把字符替换回num
                        hanlp_segmented_text_list = revert_back_to_num(
                            hanlp_segmented_text_list, generated_num_dict)

                        # 转换回原数字后，再看下里面是否还有上述预定义的key
                        predefined_keys_found = False
                        for seg in hanlp_segmented_text_list:
                            to_break = False
                            for key in num_keys_list:
                                if key in seg:
                                    predefined_keys_found = True
                                    to_break = True
                                    break
                            if to_break:
                                break

                        # 由于每个字符都已加入自定义分词字典，所以每个字符都会作为分词的整体，最终都会替换回原数字，所以下面不会出现
                        if predefined_keys_found:
                            print(
                                f'for doc_index_ {doc_index_} and doc_index_originality {doc_index_originality}, what the hanlp_segmented_text_list is after back where predefined_keys_found:')
                            pprint.pprint(hanlp_segmented_text_list)
                            print('and not the question is:')
                            pprint.pprint(question)
                            print()

                        # hanlp词性标注
                        part_of_speech_tags = tagger(hanlp_segmented_text_list)
                        # hanlp依存句法分析
                        syntactic_dependencies = syntactic_parser(
                            list(zip(hanlp_segmented_text_list, part_of_speech_tags)))

                        # hanlp依存句法分析结果的数据格式处理
                        syntactic_dependencies_list = []
                        for item in syntactic_dependencies:
                            # print(item, '\n')
                            # print(type(item))
                            # print(str(item).split('\t'))
                            syntactic_dependencies_list.append(
                                str(item).split('\t'))
                        # print('\n')

                        # 生成group_num
                        group_num, group_num_segs = generate_group_num(
                            syntactic_dependencies_list, num_list)

                        processed_dict = {
                            'id': f'{doc_index_}',
                            # 加入EDA后特有的字段，如果是原始的，则值为'raw'，否则就是追溯到原始索引序号
                            'doc_index_originality': doc_index_originality,
                            # 原始问题文本（这里统一填入EDA之前的，未经任何预处理的，test的，后处理会用到原始文本）
                            'original_text': row[1],
                            # 预处理干净的问题文本
                            'cleaned_text': question_cleaned,
                            # hanlp分词的问题文本
                            'segmented_text_new': ' '.join(hanlp_segmented_text_list),
                            # 问题文本中识别的num_list
                            'num_list': num_list,
                            # quantity cell成员索引列表
                            'group_num': group_num,
                            # quantity cell成员内容列表
                            'group_num_segs': group_num_segs,
                        }

                        if 'train' in target_file_name:
                            # 经过比较后，用来使用的表达式
                            # 都是从equation_crawled中来的
                            # 可eval，且eval的结果和更正过的train_corrected.csv中的ans相等（相等的详细比较方法见上）的equation
                            # 该equation中可能会有多余的括号()，且都是以x=开头的，且所有幂运算符都是^而不是**，且所有%都保留，未化为/100的形式
                            # 若要使用，须根据不同的方案，分别进行必要的预处理
                            processed_dict['equation'] = equation
                            # “爬”到的表达式(仅供参考、溯源)
                            processed_dict['equation_crawled'] = equation_crawled
                            # 上述表达式处理成可eval的格式(仅供参考、溯源)
                            processed_dict['equation_crawled_for_eval'] = equation_crawled_for_eval
                            # 从更正过的train_corrected.csv中拿到的答案
                            processed_dict['ans'] = ans_gold
                            # 上述答案处理成可eval的格式(仅供参考、溯源)
                            processed_dict['ans_gold_for_eval'] = ans_gold_for_eval

                        # print(
                        #     f'doc_index_: {doc_index_}, what the processed_dict is:')
                        # pprint.pprint(processed_dict)
                        # print()

                        dumped_json_str = json.dumps(
                            processed_dict, ensure_ascii=False)

                        with open(file_to_write, "a+") as f_result:
                            f_result.write(f'{dumped_json_str}\n')

                else:

                    # 使用hanlp进行分词，此时question中的数字均替换为字符
                    hanlp_segmented_text_list = pipeline_merger(question)[
                        'merged']

                    # print(
                    #     f'doc_index {doc_index}, what the hanlp_segmented_text_list is:')
                    # pprint.pprint(hanlp_segmented_text_list)
                    # print()

                    # 分完词后再把字符替换回num
                    hanlp_segmented_text_list = revert_back_to_num(
                        hanlp_segmented_text_list, generated_num_dict)

                    # print(
                    #     f'doc_index {doc_index}, what the hanlp_segmented_text_list is when reverted back to num:')
                    # pprint.pprint(hanlp_segmented_text_list)
                    # print()

                    # 转换回原数字后，再看下里面是否还有上述预定义的key
                    predefined_keys_found = False
                    for seg in hanlp_segmented_text_list:
                        to_break = False
                        for key in num_keys_list:
                            if key in seg:
                                predefined_keys_found = True
                                to_break = True
                                break
                        if to_break:
                            break

                    # 由于每个字符都已加入自定义分词字典，所以每个字符都会作为分词的整体，最终都会替换回原数字，所以下面不会出现
                    if predefined_keys_found:
                        print(
                            f'for doc_index {doc_index}, what the hanlp_segmented_text_list is after back where predefined_keys_found:')
                        pprint.pprint(hanlp_segmented_text_list)
                        print('and not the question is:')
                        pprint.pprint(question)
                        print()

                    # hanlp词性标注
                    part_of_speech_tags = tagger(hanlp_segmented_text_list)
                    # hanlp依存句法分析
                    syntactic_dependencies = syntactic_parser(
                        list(zip(hanlp_segmented_text_list, part_of_speech_tags)))

                    # hanlp依存句法分析结果的数据格式处理
                    syntactic_dependencies_list = []
                    for item in syntactic_dependencies:
                        # print(item, '\n')
                        # print(type(item))
                        # print(str(item).split('\t'))
                        syntactic_dependencies_list.append(
                            str(item).split('\t'))
                    # print('\n')

                    # 生成group_num
                    group_num, group_num_segs = generate_group_num(
                        syntactic_dependencies_list, num_list)

                    processed_dict = {
                        'id': row[0],
                        # 原始问题文本（后处理时仍须重新读取并处理）
                        'original_text': row[1],
                        # 预处理干净的问题文本
                        'cleaned_text': question_cleaned,
                        # hanlp分词的问题文本
                        'segmented_text_new': ' '.join(hanlp_segmented_text_list),
                        # 问题文本中识别的num_list
                        'num_list': num_list,
                        # quantity cell成员索引列表
                        'group_num': group_num,
                        # quantity cell成员内容列表
                        'group_num_segs': group_num_segs,
                    }

                    if 'train' in target_file_name:
                        # 经过比较后，用来使用的表达式
                        # 都是从equation_crawled中来的
                        # 可eval，且eval的结果和更正过的train_corrected.csv中的ans相等的equation
                        # 该equation中可能会有多余的括号()，且都是以x=开头的，且所有幂运算符都是^而不是**
                        # 若要使用，须根据不同的方案分别进行必要的预处理
                        processed_dict['equation'] = equation
                        # “爬”到的表达式(仅供参考、溯源)
                        processed_dict['equation_crawled'] = equation_crawled
                        # 上述表达式处理成可eval的格式(仅供参考、溯源)
                        processed_dict['equation_crawled_for_eval'] = equation_crawled_for_eval
                        # 从更正过的train_corrected.csv中拿到的答案
                        processed_dict['ans'] = ans_gold
                        # 上述答案处理成可eval的格式(仅供参考、溯源)
                        processed_dict['ans_gold_for_eval'] = ans_gold_for_eval

                    # print(
                    #     f'doc_index: {doc_index}, what the processed_dict is:')
                    # pprint.pprint(processed_dict)
                    # print()

                    dumped_json_str = json.dumps(
                        processed_dict, ensure_ascii=False)

                    with open(file_to_write, "a+") as f_result:
                        f_result.write(f'{dumped_json_str}\n')

                # if doc_index > 50:
                #     break

        counter_all = doc_index + 1

    print('counter_all: ', counter_all)
    if 'train' in target_file_name:
        print('counter_legal_doc: ', counter_legal_doc,
              'percentage: ', counter_legal_doc/counter_all)
        print('counter_can_find_equation: ', counter_can_find_equation,
              'percentage: ', counter_can_find_equation/counter_all)
        print('counter_can_find_equation_from_crawled: ', counter_can_find_equation_from_crawled,
              'percentage: ', counter_can_find_equation_from_crawled/counter_all)
    if (use_eda > 0) and (platform.system().lower() == 'linux'):
        print(f'for use_eda {use_eda}, EDA amount: ', doc_index_eda - doc_index_eda_start,
              'per question(legal doc): ', (doc_index_eda - doc_index_eda_start)/counter_legal_doc)
    print()
