#coding:utf-8
import pymysql, json, time, re, pickle, os, math, requests, os
import jieba_fast as jieba
#import jieba #用windows跑的时候请在读文件的时候加上encoding参数并修改jieba库的使用
jieba.initialize()
from key import DBS, MAX_NUM, MAX_FREQ, PATH, PATH_B, SQL
from io import StringIO
import pandas as pd
from collections import Counter

black_list = []
if os.path.exists(PATH_B):
    black_list = open(PATH_B, "r").read()
    black_list = black_list.split("\n")
else:
    black_list = [""]
filtrate = re.compile(u'[\u4e00-\u9fa5A-Za-z0-9]')
final_result = {}
for name in DBS.keys():
    conn = pymysql.connect(DBS[name]["DBPATH"], DBS[name]["USER"], DBS[name]["PWD"], DBS[name]["DB"],charset='utf8')
    curs = conn.cursor()
    curs.execute(SQL[0])
    companies = curs.fetchall()
    companies = [i[0] for i in companies]
    currencies = {}
    t1=time.time()
    
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
            
            ## 区别之前的写法主要改动是因为之前的最后top50计算有问题。每个分组的top50 和全部数据的top50 不能简单合并。比如10个数据 5个一组分2次
            ## 有一个词在第一组有一次出现 第二组有10次出现。那么第一组的top50里可能就没有这个词了，再和第二组合并的时候会导致数量不对。另外之前
            ## 版本的最后合并会使得总词量大于50个，不符合要求。 所以新版采用先合并所有的字符串再最后统一分词统计。
            all_name = Counter()
            all_memo = Counter()
            for k in range(loop):  
                processed = ["", ""]
                raw_content=pd.read_sql_query(SQL[3],params=[i, j, k*MAX_NUM, MAX_NUM],con=conn)
                ##raw_content = curs.fetchall()
                ## python简单拼接字符串的效率在字符串超长的时候极低参考https://www.cnblogs.com/heshizhu/archive/2012/01/11/2319892.html
                ## 目前的处理方法虽然在数量极大的时候依然可能爆内存，但从实际角度目前问题不大 TODO 分批处理
                
                ## 也可以采用sql语言直接拼接select group_concat(CUSTOMER_ACCOUNT_NAME separator ' ') as t from c 不过一般受限于数据库系统配置
                ## 并不太合适。
                '''
                file1 = StringIO()
                file2 = StringIO()
                for raw in raw_content:
                    if raw[0] != "NONE" and raw[0] != None:
                        file1.write(raw[0] + "\n") #分隔符换为\n可以更好的利用jieba的并行处理
                        
                    if raw[1] != "NONE" and raw[1] != None:
                        file2.write(raw[1] + "\n")
                '''
                processed[0] = ' '.join(raw_content['name']) 
                processed[1] = ' '.join(raw_content['memo'])
                processed = [jieba.lcut(proc) for proc in processed]
                #processed = [list(filter(lambda x: re.search(filtrate, x) == None, proc)) for proc in processed]
                # 在这里过滤特殊字符非常费时，移到最后输出前处理
                word_name = Counter(dict(Counter(processed[0]).most_common()))
                word_memo = Counter(dict(Counter(processed[1]).most_common()))
                all_name += word_name
                all_memo += word_memo
            
            
            
            if len(all_name)>0:
                for w in all_name.most_common():
                    if (w[0] not in black_list) and (re.search(filtrate, w[0]) != None):
                        currencies[uid]["name"].update([w])
                    if len(currencies[uid]["name"]) == MAX_FREQ:
                        break
            if len(all_memo)>0:
                for w in all_memo.most_common():
                    if (w[0] not in black_list) and (re.search(filtrate, w[0]) != None):
                        currencies[uid]["memo"].update([w])
                    if len(currencies[uid]["memo"]) == MAX_FREQ:
                        break
            
             
            
            
    final_result[name] = currencies
pickle.dump(final_result, open(PATH, "wb"), protocol=2)
requests.get("http://127.0.0.1:5000/reload")
t2=time.time()
with open("/tmp/test.txt", "a") as ff:
    ff.write(str(t2-t1)+"\n")
conn.close()