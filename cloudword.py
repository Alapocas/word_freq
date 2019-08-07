#coding:utf-8
import pymysql, json, time, re, pickle, os, collections, math, requests, os
import jieba_fast as jieba
#import jieba #用windows跑的时候请在读文件的时候加上encoding参数并修改jieba库的使用
jieba.initialize()
from key import DBS, MAX_NUM, MAX_FREQ, PATH, PATH_B, SQL
black_list = []
if os.path.exists(PATH_B):
    black_list = open(PATH_B, "r").read()
    black_list = black_list.split("\n")
else:
    black_list = [""]
filtrate = re.compile(u'[^\u4e00-\u9fa5A-Za-z]+')
final_result = {}
for name in DBS.keys():
    conn = pymysql.connect(DBS[name]["DBPATH"], DBS[name]["USER"], DBS[name]["PWD"], DBS[name]["DB"],charset='utf8')
    curs = conn.cursor()
    curs.execute(SQL[0])
    companies = curs.fetchall()
    companies = [i[0] for i in companies]
    currencies = {}
    t1=time.time()
    jieba.enable_parallel() #线程不是开得越多越好，得按需求来
    for i in companies:
        curs.execute(SQL[1], [i])
        currency = curs.fetchall()
        if len(currency)>0:
            currency = [i[0] for i in currency]
        for j in currency:
            curs.execute(SQL[2], [i, j])
            num_of_rows = curs.fetchall()[0][0]
            loop = math.ceil(num_of_rows/MAX_NUM)
            if loop == 0:
                break
            uid = str(i)+','+j
            currencies[uid] = {"name": {}, "memo": {}}
            for k in range(loop):
                curs.execute(SQL[3], [i, j, k*MAX_NUM, MAX_NUM])
                raw_content = curs.fetchall()
                currency = {"name": {}, "memo": {}}
                processed = ["", ""]
                for raw in raw_content:
                    if raw[0] != "NONE" and raw[0] != None:
                        processed[0] += raw[0] + " "
                    if raw[1] != "NONE" and raw[1] != None:
                        processed[1] += raw[1] + " "
                processed = [jieba.lcut(proc.strip()) for proc in processed]
                processed = [list(filter(lambda x: re.search(filtrate, x) == None, proc)) for proc in processed]
                words = collections.Counter(processed[0]).most_common()
                position = 0
                while True:
                    if position == len(words) or len(currency["name"]) == 50:
                        break
                    elif words[position][0] not in black_list:
                        currency["name"].update([words[position]])
                    position += 1
                words = collections.Counter(processed[1]).most_common()
                position = 0
                while True:
                    if position == len(words) or len(currency["memo"]) == 50:
                        break
                    elif words[position][0] not in black_list:
                        currency["memo"].update([words[position]])
                    position += 1
                for key, value in currency["name"].items():
                    if key in currencies[uid]["name"]:
                        currencies[uid]["name"][key] += value
                    else:
                        currencies[uid]["name"][key] = value
                for key, value in currency["memo"].items():
                    if key in currencies[uid]["memo"]:
                        currencies[uid]["memo"][key] += value
                    else:
                        currencies[uid]["memo"][key] = value
    final_result[name] = currencies
pickle.dump(final_result, open(PATH, "wb"), protocol=2)
requests.get("http://127.0.0.1:5000/reload")
t2=time.time()
with open("/tmp/test.txt", "a") as ff:
    ff.write(str(t2-t1)+"\n")
conn.close()