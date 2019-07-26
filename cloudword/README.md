# 数据库词频统计工具

## 目的

脚本从数据库提取公司对账单里流水的对手方名称和用户备注，按本方ID分类。然后使用jieba分词并统计词频，生成词频字典保存至本地等待调用。api获得本方ID和查看条目作为参数，然后通过路径找到保存的词频字典，返回对应的词频。

## 依赖

- flask_restful
- collections
- jieba_fast (在windows下请用jieba并关闭enable_paralle())
- pymysql
- request
- pickle
- flask
- time
- json
- os
- re

## cloudword.py的使用

全局参数，请按情况自行填写：

- DBPATH：数据库路径
- USER：数据库用户名
- PWD：数据库用户密码
- DB：数据库名称
- MAX_NUM=最多取多少条数据作词频统计
- MAX_FREQ=词频最多取前几
- PATH=词频字典的存储路径

词频统计处理会按照本方ID进行，每完成一个本方ID的词频统计就会重新更新存储。

在Linux系统下，请调用jieba_fast库并开启多线程模式（jieba.enable_parallel()），分词速度会更快；在Windows系统下，请调用jieba库并关闭多线程模式

## API的调用

在使用api之前，请先确保跑过一遍cloudword.py，否则api将无法使用路径提取词频字典。

请求格式：POST， json

- **/frequency**
  - 请求json样例：{“id”：“133”，“method”：“name”} “id”为本方ID，“method”为查看条目：“name”为查看对手方名称词频，“memo”为查看用户备注词频。
  - 返回json样例：{"上海": 1, "爱信诺": 1, "航天": 1, "信息": 1, "有限公司": 1}

## 测试

python 2.7.15+, python 3.6.5 环境下都可以

打开test.py， run， 输出：{"差旅费": 2, "网络": 2, "转账": 2, "WFP": 1, "公积金": 1, "其他": 1}。