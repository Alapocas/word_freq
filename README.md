# 数据库词频统计工具

## 目的

脚本从数据库提取公司对账单里流水的对手方名称和用户备注，按本方ID分类。然后使用jieba分词并统计词频，生成词频字典保存至本地等待调用。api获得本方ID和查看条目作为参数，然后通过路径找到保存的词频字典，返回对应的词频。

cloudword的定时执行：使用linux的crontab命令每天定时更新一次词典

wordc_api的后台运行：可以使用supervisor配置文件在后台自动执行python flask

## 依赖

- flask_restful
- collections
- flask_cors
- jieba_fast (在windows下请用jieba并关闭enable_paralle())
- requests
- pymysql
- pickle
- flask
- re

## cloudword.py的使用

全局参数，请按情况自行填写：

- 数据库字典的格式：{名称：{“DBPATH”：数据库路径，“USER”：数据库用户名，“PWD”：数据库用户密码，“DB”：数据库名称}}
- DBS：数据库字典集
- MAX_NUM=最多取多少条数据作词频统计
- MAX_FREQ=词频最多取前几
- PATH=词频字典的存储路径
- PATH_B=黑名单文件的绝对路径

词频统计处理会按照本方ID进行，每完成一个本方ID的词频统计就会重新更新存储。

在Linux系统下，请调用jieba_fast库并开启多线程模式（jieba.enable_parallel()），分词速度会更快；在Windows系统下，请调用jieba库并关闭多线程模式

请在cloudword.py同层级下创建black_list.txt，格式为每行一个黑名单词汇。

## API的调用

在使用api之前，请先确保跑过一遍cloudword.py，否则api将无法使用路径提取词频字典。

请求格式：POST， json

- **/frequency**
  - 请求json样例：{“source”：”GO“，“id”：“133”，“currency”：“CNY”，“method”：“name”} ”source“为数据库，“id”为本方ID，“currency”为账户币种，“method”为查看条目：“name”为查看对手方名称词频，“memo”为查看用户备注词频。
  - 返回json样例：{“code": 200, "data": {"上海": 1, "爱信诺": 1, "航天": 1, "信息": 1, "有限公司": 1}}

## 测试

python 2.7.15+, python 3.6.5 环境下都可以

命令窗口或supervisor后台运行wordc_api.py，然后有两种方法

1. 服务器输入curl http://127.0.0.1:5000/frequency?source=GO\&id=133,CNY\&method=name， 输出：{"code": 200, "data": {...词频字典...}}。
2. 运行同层级下test.py

返回“code"：500的原因：

1. ”data”：“Invalid database request!“     输入的source不存在于配置文件key.py的字典集中
2. ”data”：“Invalid company id or command!“     输入的id、币种、或方式不存在，请确保id和币种的搭配是有效的，方式请填写”name”或者“memo”中的一个