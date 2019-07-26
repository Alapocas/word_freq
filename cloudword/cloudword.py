#coding:utf-8
import pymysql, json, time, re, pickle, os, collections
#import jieba_fast as jieba
import jieba #用windows跑的时候请在读文件的时候加上encoding参数并修改jieba库的使用
jieba.initialize()
filtrate = re.compile(u'[^\u4e00-\u9fa5A-Za-z]+')
DBPATH="localhost"
USER="root"
PWD="123456"
DB="test"
MAX_NUM=10000
MAX_FREQ=50
PATH=os.path.dirname(__file__)+"/total.pickle"
conn = pymysql.connect(DBPATH, USER, PWD, DB)
curs = conn.cursor()
curs.execute("SELECT DISTINCT LE_ID FROM c4c_bank_statement")
result = curs.fetchall()
result = [i[0] for i in result]
total = {}
t1=time.time()
#jieba.enable_parallel() #线程不是开得越多越好，得按需求来
for i in result:
    curs.execute("SELECT CUSTOMER_ACCOUNT_NAME, USER_MEMO FROM c4c_bank_statement WHERE LE_ID = %s LIMIT %s", [i, MAX_NUM])
    res = curs.fetchall()
    total[str(i)] = {}
    total[str(i)]["name"] = dict(collections.Counter([j for j in jieba.lcut(" ".join([k[0] for k in res if k != "NONE"])) if re.search(filtrate, j) == None]).most_common(MAX_FREQ))
    total[str(i)]["memo"] = dict(collections.Counter([j for j in jieba.lcut(" ".join([k[1] for k in res if k != None])) if re.search(filtrate, j) == None]).most_common(MAX_FREQ))
    print(total[str(i)])
    pickle.dump(total, open(PATH, "wb"), protocol=2) #protocol参数是为了确保pickle文件能在python2环境下打开
t2=time.time()
print(t2-t1)
conn.close()
