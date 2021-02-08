import csv
import os
import pprint

from tqdm import tqdm

corrected_dict = {}

with open('../official_data/错误修订/train文件中题目错误修订.csv', 'r') as f:
    reader = csv.reader(f)
    for row in tqdm(reader):
        doc_index = row[0]
        question = row[1]
        ans = row[2]
        corrected_dict[doc_index] = {
            'question': question,
            'ans': ans,
            'type': 0,
        }

with open('../official_data/错误修订/train文件中答案错误修订.csv', 'r') as f:
    reader = csv.reader(f)
    for row in tqdm(reader):
        doc_index = row[0]
        question = row[1]
        ans = row[2]
        corrected_dict[doc_index] = {
            'question': question,
            'ans': ans,
            'type': 1,
        }

print('what the corrected_dict is:')
# pprint.pprint(corrected_dict)
print('and its length is:')
pprint.pprint(len(corrected_dict))
print()

train_corrected_f = open('train_corrected.csv', 'w', encoding='utf-8')
csv_writer_train_corrected = csv.writer(train_corrected_f)


with open('../official_data/train.csv', 'r') as f:
    reader = csv.reader(f)

    for row in tqdm(reader):
        doc_index = row[0]
        question = row[1]
        ans = row[2]
        # print(doc_index, question, ans)

        if int(doc_index) == 6886:
            csv_writer_train_corrected.writerow(
                [doc_index, '一本书一页有21行，每行28个字。估计一下，这一页大约有多少个字？', 588])
        elif int(doc_index) == 8662:
            csv_writer_train_corrected.writerow(
                [doc_index, '两袋白砂糖，甲袋的重量是乙袋的1.4倍，如果乙袋增加8千克，两袋糖就一样重，原来每袋糖共多少千克', 48])
        elif int(doc_index) == 10794:
            csv_writer_train_corrected.writerow(
                [doc_index, '小华带着自己的爱犬去姥姥家，已知小华步行的速度是每分钟80米，犬的速度每分钟300米。她和犬同时从家里出发，犬跑到姥姥家后马上调头找小华，和小华相遇后又马上调头跑向姥姥家，就这样犬来回的跑。小华到姥姥家共用时15分钟，由此可知小华家离姥姥家多少米，犬跑了多少米？', 4500])
        elif int(doc_index) == 10838:
            csv_writer_train_corrected.writerow(
                [doc_index, '甲乙两车同时从相距506千米的两地相向开出，甲车每小时行52千米，乙车每小时行40千米，那么几小时后两车相距158千米？', '87/23'])
        elif int(doc_index) == 7175:
            csv_writer_train_corrected.writerow(
                [doc_index, '一把椅子60元，250元最多能买几把椅子？', 4])
        elif doc_index in corrected_dict:
            csv_writer_train_corrected.writerow(
                [doc_index, corrected_dict[doc_index]['question'], corrected_dict[doc_index]['ans']])
            # print(doc_index, corrected_dict[doc_index]
            #       ['question'], corrected_dict[doc_index]['ans'])
        else:
            csv_writer_train_corrected.writerow(
                [doc_index, question, ans])

with open('train_corrected.csv', 'r') as f:
    reader = csv.reader(f)

    for row in tqdm(reader):
        doc_index = row[0]
        question = row[1]
        ans = row[2]
        if ';' in f'{ans}':
            print(doc_index, question, ans)
