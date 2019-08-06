#coding:utf-8
import pymysql, json, time, re, pickle, os, collections, math, requests
import jieba_fast as jieba
#import jieba #用windows跑的时候请在读文件的时候加上encoding参数并修改jieba库的使用
jieba.initialize()
from key import DBS, MAX_NUM, MAX_FREQ, PATH, SQL
filtrate = re.compile(u'[^\u4e00-\u9fa5A-Za-z]+')
final = {}
for name in DBS.keys():
    conn = pymysql.connect(DBS[name]["DBPATH"], DBS[name]["USER"], DBS[name]["PWD"], DBS[name]["DB"],charset='utf8')
    curs = conn.cursor()
    curs.execute(SQL[0])
    result = curs.fetchall()
    result = [i[0] for i in result]
    total = {}
    t1=time.time()
    jieba.enable_parallel() #线程不是开得越多越好，得按需求来
    for i in result[:30]:
        curs.execute(SQL[1], [i])
        currency = curs.fetchall()
        if len(currency)>0:
            currency = [i[0] for i in currency]
        for j in currency:
            curs.execute(SQL[2], [i, j])
            info_num = curs.fetchall()[0][0]
            loop = math.ceil(info_num/MAX_NUM)
            if loop == 0:
                break
            uid = str(i)+','+j
            total[uid] = {"name":{}, "memo":{}}
            for k in range(loop):
                curs.execute(SQL[3], [i, j, k*MAX_NUM, MAX_NUM])
                res = curs.fetchall()
                tmp = {}
                tmp["name"] = dict(collections.Counter([word for word in jieba.lcut(" ".join([raw[0] for raw in res if raw != "NONE"])) if re.search(filtrate, word) == None]).most_common(MAX_FREQ))
                tmp["memo"] = dict(collections.Counter([word for word in jieba.lcut(" ".join([raw[1] for raw in res if raw != None])) if re.search(filtrate, word) == None]).most_common(MAX_FREQ))
                for key, value in tmp["name"].items():
                    if key in total[uid]["name"]:
                        total[uid]["name"][key] += value
                    else:
                        total[uid]["name"][key] = value
                for key, value in tmp["memo"].items():
                    if key in total[uid]["memo"]:
                        total[uid]["memo"][key] += value
                    else:
                        total[uid]["memo"][key] = value
    final[name] = total
    print(final)
pickle.dump(final, open(PATH, "wb"), protocol=2)
requests.get("http://127.0.0.1:5000/reload")
t2=time.time()
with open("/tmp/test.txt", "a") as ff:
    ff.write(str(t2-t1)+"\n")
conn.close()