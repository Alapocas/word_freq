import os
GO = {"DBPATH":"", "USER":"", "PWD":"", "DB":""}#数据库信息
DBS = {"GO":GO}#数据库字典
MAX_NUM = 30000 #最多条数
MAX_FREQ = 50 #词频排行上限
PATH = ""#字典的绝对路径
PATH_B = ""#黑名单文件的绝对路径
SQL = ["SELECT DISTINCT enterprise_id FROM tb_enterprise_entity", "SELECT ba.currency FROM c4c_bank_account ba INNER JOIN tb_enterprise_entity tee ON tee.le_id = ba.le_id AND tee.enterprise_id = %s GROUP BY ba.currency", "SELECT COUNT(*) FROM c4c_bank_statement a INNER JOIN tb_enterprise_entity b on a.LE_ID = b.le_id WHERE enterprise_id = %s and CURRENCY = %s", "SELECT CUSTOMER_ACCOUNT_NAME as name, USER_MEMO as memo FROM c4c_bank_statement a INNER JOIN tb_enterprise_entity b on a.LE_ID = b.le_id WHERE enterprise_id = %s and CURRENCY = %s LIMIT %s, %s"]