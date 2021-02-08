# coding: utf-8
import json
import os
import pickle
import pprint
import random
import time

import torch.optim
from tqdm import tqdm, trange

from graph_to_tree_utils import (TRAIN_ITERATION_OVER, USE_EDA, batch_size,
                                 beam_size, embedding_size, hidden_size,
                                 learning_rate, n_epochs, n_layers,
                                 weight_decay)
from src.expressions_transfer import *
from src.models import *
from src.train_and_evaluate import *

if not os.path.exists('models'):
    os.system('mkdir models')

if not os.path.exists('prepared_data'):
    os.system('mkdir prepared_data')

random.seed(42)
train_iteration_over = TRAIN_ITERATION_OVER


if (not os.path.exists('prepared_data/generate_num_ids.pkl')) and (not os.path.exists('prepared_data/input_lang.pkl')):

    data_train = load_raw_data(
        "group_num_processed/train_corrected_processed_eda.json", raw=False, operator_no_gt_thresh=4, use_eda=USE_EDA)


test_file_name = 'test'

if (not os.path.exists('prepared_data/generate_num_ids.pkl')) and (not os.path.exists('prepared_data/input_lang.pkl')):

    data_test = []

    # 路径根据实际情况调整
    target_file = f'./group_num_processed/{test_file_name}_processed.json'

    for doc_index, data_d in tqdm(enumerate(open(target_file))):
        data_d = json.loads(data_d)

        # 初始化找到的分数集合
        fraction_num_set = set()
        # 将segmented_text_new转为列表
        segmented_text_new_list = data_d["segmented_text_new"].split(
            ' ')
        # 遍历segmented_text_new_list列表，发现分数的直接加括号，并将发现的分数添加到上述集合中
        for i_, item in enumerate(segmented_text_new_list):
            if ('/' in item) and (item[0] in digits) and (item[-1] in digits):
                fraction_num_set.add(item)
                segmented_text_new_list[i_] = f'({item})'
        # 将segmented_text_new重新组合成字符串
        data_d["segmented_text_new"] = (
            ' '.join(segmented_text_new_list)).strip()

        # 将发现的分数集合转成列表，并排序（倒序）
        fraction_num_list = list(fraction_num_set)
        fraction_num_list.sort(key=lambda x: len(x), reverse=True)

        # 这里之所以不直接对发现的分数进两端加括号，是为了防止出现，如果题中同时有1/5和11/5，11/5变为(11/5)之后又变为(1(1/5))
        fraction_num_list_ext = []
        for item in fraction_num_list:
            numerator = item.split('/')[0]
            denominator = item.split('/')[1]
            fraction_num_list_ext.append(
                (item, f'({numerator}圀/圀{denominator})'))

        for fraction_num, fraction_num_ext in fraction_num_list_ext:
            data_d["cleaned_text"] = data_d["cleaned_text"].replace(
                fraction_num, fraction_num_ext)

        # 再把多余的占位符 圀 去掉
        data_d["cleaned_text"] = data_d["cleaned_text"].replace('圀', '')

        # 进行覆盖
        data_d["original_text"] = data_d["cleaned_text"]
        data_d["segmented_text"] = data_d["segmented_text_new"]

        data_d["equation"] = ''
        # 因为测试数据都不知道答案，所以此处都给-1000
        data_d["ans"] = -1000

        data_test.append(data_d)

    print('what the first 10 items of data_test is:')
    pprint.pprint(data_test[:10])
    print('and its original length is:')
    pprint.pprint(len(data_test))
    print()

if (not os.path.exists('prepared_data/generate_num_ids.pkl')) and (not os.path.exists('prepared_data/input_lang.pkl')):
    pairs, generate_nums, copy_nums = transfer_num(
        data_train + data_test, raw=False)

    print('what the first 10 items of pairs are:')
    pprint.pprint(pairs[:10])
    print('and the last item of pairs is:')
    pprint.pprint(pairs[-1])
    print('and its original length is:')
    pprint.pprint(len(pairs))
    print()

    pickle.dump(generate_nums, open('prepared_data/generate_nums.pkl', 'wb'))
    pickle.dump(copy_nums, open('prepared_data/copy_nums.pkl', 'wb'))

else:
    generate_nums = pickle.load(open('prepared_data/generate_nums.pkl', 'rb'))
    copy_nums = pickle.load(open('prepared_data/copy_nums.pkl', 'rb'))
    print(f'generate_nums loaded!\n')
    print(f'copy_nums loaded!\n')

print('what the generate_nums are:')
pprint.pprint(generate_nums)
print('and its original length is:')
pprint.pprint(len(generate_nums))
print()

print('what the copy_nums are:')
pprint.pprint(copy_nums)
print()

if (not os.path.exists('prepared_data/generate_num_ids.pkl')) and (not os.path.exists('prepared_data/input_lang.pkl')):
    temp_pairs = []
    for p in pairs:
        temp_pairs.append((p[0], from_infix_to_prefix(p[1]), p[2], p[3], p[4]))
    pairs = temp_pairs


if (not os.path.exists('prepared_data/generate_num_ids.pkl')) and (not os.path.exists('prepared_data/input_lang.pkl')):
    # random.shuffle(pairs)
    # pairs_tested = pairs[:int(len(pairs) * 0.1)]
    # pairs_trained = pairs[int(len(pairs) * 0.1):]

    pairs_trained = pairs[:len(data_train)]
    pairs_tested = pairs[len(data_train):]

    print('len(pairs_tested): ', len(pairs_tested))
    print('len(pairs_trained): ', len(pairs_trained))
    print()

    assert len(pairs_tested) == len(data_test)
    assert len(pairs_tested) == 8000

    random.shuffle(pairs_trained)


if not os.path.exists('prepared_data/input_lang.pkl'):
    input_lang, output_lang, train_pairs, test_pairs = prepare_data(pairs_trained, pairs_tested, 5, generate_nums,
                                                                    copy_nums, tree=True)
    pickle.dump(input_lang, open('prepared_data/input_lang.pkl', 'wb'))
    pickle.dump(output_lang, open('prepared_data/output_lang.pkl', 'wb'))
    pickle.dump(train_pairs, open('prepared_data/train_pairs.pkl', 'wb'))
    pickle.dump(test_pairs, open('prepared_data/test_pairs.pkl', 'wb'))

else:
    input_lang = pickle.load(open('prepared_data/input_lang.pkl', 'rb'))
    output_lang = pickle.load(open('prepared_data/output_lang.pkl', 'rb'))
    train_pairs = pickle.load(open('prepared_data/train_pairs.pkl', 'rb'))
    test_pairs = pickle.load(open('prepared_data/test_pairs.pkl', 'rb'))
    print(f'prepared data loaded!\n')

# print('train_pairs[0]')
# print(train_pairs[0])
# exit()


if not os.path.exists('prepared_data/generate_num_ids.pkl'):
    generate_num_ids = []
    for num in generate_nums:
        generate_num_ids.append(output_lang.word2index[num])

    print('what the first 10 items of generate_num_ids are:')
    pprint.pprint(generate_num_ids[:10])
    print('and its original length is:')
    pprint.pprint(len(generate_num_ids))
    print()

    pickle.dump(generate_num_ids, open(
        'prepared_data/generate_num_ids.pkl', 'wb'))

else:
    generate_num_ids = pickle.load(
        open('prepared_data/generate_num_ids.pkl', 'rb'))
    print(f'generated num ids loaded!\n')

# Initialize models
encoder = EncoderSeq(input_size=input_lang.n_words, embedding_size=embedding_size, hidden_size=hidden_size,
                     n_layers=n_layers)
predict = Prediction(hidden_size=hidden_size, op_nums=output_lang.n_words - copy_nums - 1 - len(generate_nums),
                     input_size=len(generate_nums))
generate = GenerateNode(hidden_size=hidden_size, op_nums=output_lang.n_words - copy_nums - 1 - len(generate_nums),
                        embedding_size=embedding_size)
merge = Merge(hidden_size=hidden_size, embedding_size=embedding_size)
# the embedding layer is  only for generated number embeddings, operators, and paddings

encoder_optimizer = torch.optim.Adam(
    encoder.parameters(), lr=learning_rate, weight_decay=weight_decay)
predict_optimizer = torch.optim.Adam(
    predict.parameters(), lr=learning_rate, weight_decay=weight_decay)
generate_optimizer = torch.optim.Adam(
    generate.parameters(), lr=learning_rate, weight_decay=weight_decay)
merge_optimizer = torch.optim.Adam(
    merge.parameters(), lr=learning_rate, weight_decay=weight_decay)

encoder_scheduler = torch.optim.lr_scheduler.StepLR(
    encoder_optimizer, step_size=20, gamma=0.5)
predict_scheduler = torch.optim.lr_scheduler.StepLR(
    predict_optimizer, step_size=20, gamma=0.5)
generate_scheduler = torch.optim.lr_scheduler.StepLR(
    generate_optimizer, step_size=20, gamma=0.5)
merge_scheduler = torch.optim.lr_scheduler.StepLR(
    merge_optimizer, step_size=20, gamma=0.5)

# Move models to GPU
if USE_CUDA:
    encoder.cuda()
    predict.cuda()
    generate.cuda()
    merge.cuda()

if not train_iteration_over:

    if os.path.exists('training_memo.pkl'):

        training_memo = pickle.load(open('training_memo.pkl', 'rb'))
        trained_epoches = training_memo['trained_epoches']
    else:
        trained_epoches = -1

    if os.path.exists('models/encoder'):
        encoder.load_state_dict(torch.load("models/encoder"))
        predict.load_state_dict(torch.load("models/predict"))
        generate.load_state_dict(torch.load("models/generate"))
        merge.load_state_dict(torch.load("models/merge"))
        print('models loaded before entering the training iteration! Now the memo is:')
        print('training_memo: ', training_memo)
        print()

    for epoch in range(n_epochs):

        if epoch <= trained_epoches:
            continue

        loss_total = 0
        input_batches, input_lengths, output_batches, output_lengths, nums_batches, \
            num_stack_batches, num_pos_batches, num_size_batches, num_value_batches, graph_batches = prepare_train_batch(
                train_pairs, batch_size)
        print("epoch:", epoch + 1)
        start = time.time()
        for idx in trange(len(input_lengths)):

            try:
                loss = train_tree(
                    input_batches[idx], input_lengths[idx], output_batches[idx], output_lengths[idx],
                    num_stack_batches[idx], num_size_batches[idx], generate_num_ids, encoder, predict, generate, merge,
                    encoder_optimizer, predict_optimizer, generate_optimizer, merge_optimizer, output_lang, num_pos_batches[idx], graph_batches[idx])
            except BaseException as e:

                if not isinstance(e, KeyboardInterrupt):
                    print(f'idx: {idx}')
                    print('input_batches[idx]:')
                    pprint.pprint(input_batches[idx])
                    print()

                    input_batches_2_words = list(
                        map(lambda x: list(map(lambda y: input_lang.index2word[y], x)), input_batches[idx]))

                    print('input_batches_2_words:')
                    pprint.pprint(input_batches_2_words)
                    print()

                    print('input_lengths[idx]:')
                    pprint.pprint(input_lengths[idx])
                    print()
                    print('output_batches[idx]:')
                    pprint.pprint(output_batches[idx])
                    print()

                    output_batches_2_words = list(
                        map(lambda x: list(map(lambda y: output_lang.index2word[y], x)), output_batches[idx]))

                    print('output_batches_2_words:')
                    pprint.pprint(output_batches_2_words)
                    print()

                    print('output_lengths[idx]:')
                    pprint.pprint(output_lengths[idx])
                    print()

                    # print('num_stack_batches[idx]:')
                    # pprint.pprint(num_stack_batches[idx])
                    # print()
                    # print('num_size_batches[idx]:')
                    # pprint.pprint(num_size_batches[idx])
                    # print()
                    # print('num_pos_batches[idx]:')
                    # pprint.pprint(num_pos_batches[idx])
                    # print()
                    # print('graph_batches[idx]:')
                    # pprint.pprint(graph_batches[idx])
                    # print()

                raise Exception('Some error happened!\n')

            loss_total += loss

        # https://zhuanlan.zhihu.com/p/104472245
        # /usr/local/lib/python3.6/dist-packages/torch/optim/lr_scheduler.py:114: UserWarning: Seems like `optimizer.step()` has been overridden after learning rate scheduler initialization. Please, make sure to call `optimizer.step()` before `lr_scheduler.step()`. See more details at https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate
        # "https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate", UserWarning)
        encoder_scheduler.step()
        predict_scheduler.step()
        generate_scheduler.step()
        merge_scheduler.step()

        print("loss:", loss_total / len(input_lengths))
        print("training time", time_since(time.time() - start))
        print("--------------------------------")

        if (epoch+1) % 10 == 0:
            torch.save(encoder.state_dict(), "models/encoder")
            torch.save(predict.state_dict(), "models/predict")
            torch.save(generate.state_dict(), "models/generate")
            torch.save(merge.state_dict(), "models/merge")
            print(f'models saved for epoch {epoch+1}!\n')

            training_memo = {
                'competiton_data_source': test_file_name,
                'trained_epoches': epoch,
            }

            if os.path.exists('training_memo.pkl'):
                os.system(f'rm -rf training_memo.pkl')

            pickle.dump(training_memo, open('training_memo.pkl', 'wb'))

    # 训练结束后最后一次保存
    torch.save(encoder.state_dict(), "models/encoder")
    torch.save(predict.state_dict(), "models/predict")
    torch.save(generate.state_dict(), "models/generate")
    torch.save(merge.state_dict(), "models/merge")
    print(
        f'models saved after the training iteration over, now the epoch is {epoch+1}!\n')

    training_memo = {
        'competiton_data_source': test_file_name,
        'trained_epoches': epoch,
    }

    if os.path.exists('training_memo.pkl'):
        os.system(f'rm -rf training_memo.pkl')

    pickle.dump(training_memo, open('training_memo.pkl', 'wb'))

else:
    encoder.load_state_dict(torch.load("models/encoder"))
    predict.load_state_dict(torch.load("models/predict"))
    generate.load_state_dict(torch.load("models/generate"))
    merge.load_state_dict(torch.load("models/merge"))
    print('models loaded when training iteration is over!\n')

encoder.eval()
predict.eval()
generate.eval()
merge.eval()
print('models set as eval()!\n')


predict_total = 0
predicted_list = []
# 一个特例：由于分词的原因，而造成的num_list中有分母为0的成员
div_by_0_index_list = [4715]


start = time.time()
for test_batch_index, test_batch in enumerate(tqdm(test_pairs)):

    if (len(div_by_0_index_list) > 0) and (test_batch_index in div_by_0_index_list):
        predicted_list.append({
            'question_index': test_batch_index,
            'prefix_expr': [],
        })
        continue

    print_cond = test_batch_index < 10

    # print(test_batch)
    batch_graph = get_single_example_graph(
        test_batch[0], test_batch[1], test_batch[7], test_batch[4], test_batch[5])
    test_res = evaluate_tree(test_batch[0], test_batch[1], generate_num_ids, encoder, predict, generate,
                             merge, output_lang, test_batch[5], batch_graph, beam_size=beam_size)

    if print_cond:
        print(
            f'for test_batch_index: {test_batch_index}, what the test_res is:')
        pprint.pprint(test_res)
        print()

    _, _, prefix_expr_predicted, _ = compute_prefix_tree_result(
        test_res, test_batch[2], output_lang, test_batch[4], test_batch[6])

    if print_cond:
        print(
            f'for test_batch_index: {test_batch_index}, what the prefix_expr_predicted is:')
        pprint.pprint(prefix_expr_predicted)
        print()

    predicted_list.append({
        'question_index': test_batch_index,
        'prefix_expr': prefix_expr_predicted,
    })

    predict_total += 1

print("predict_total", predict_total)
print("predicting time", time_since(time.time() - start))
print("------------------------------------------------------")


print('what the first 10 items of predicted_list are at last:')
pprint.pprint(predicted_list[:10])
print('and its original length is:')
pprint.pprint(len(predicted_list))
print()

print('assert 1\n')
assert len(predicted_list) == len(test_pairs)

if os.path.exists('predicted_list.pkl'):
    os.system('rm -f predicted_list.pkl')

if not os.path.exists('predicted_list.pkl'):
    pickle.dump(predicted_list, open('predicted_list.pkl', 'wb'))
