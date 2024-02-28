'''
本文件是由于od系统没有留存拼好饭数据，所以在美团下载的拼好饭数据，更新到数据库里
'''

import pymysql
import pandas as pd
import os
import datetime

# 1. 连接 MySQL 数据库
conn = pymysql.connect(host='localhost', user='root', password='123456', database='every_day')
cursor = conn.cursor()

filepath = '拼好饭数据更新留存'
filelist = os.listdir('../'+filepath)
file_temp = []
for i in filelist:
    print(i)
    df = pd.read_csv('../'+filepath + '/' + i, encoding='ANSI')
    df['日期'] = df['日期'].astype(str)
    df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d').dt.date
    df = df.dropna(axis=0)
    # date_obj = datetime.datetime.strptime(df['日期'], "%Y%m%d")

    for _, row in df.iterrows():
        date = row['日期']
        id = row['门店id']
        impressions = row['拼好饭曝光人数']
        in_store_visits = row['拼好饭入店人数']
        orders = row['拼好饭下单人数']
        in_store_rate = row['拼好饭入店转化率']
        order_rate = row['拼好饭下单转化率']
        sql_statement = f"""UPDATE every_day 
                            SET `拼好饭-曝光人数`={impressions}, `拼好饭-到店人数`={in_store_visits}, `拼好饭-下单人数`={orders}, 
                            `拼好饭-入店转化率`={in_store_rate}, `拼好饭-下单转化率`={order_rate}
                            WHERE 日期='{date}' and 平台店铺id = '{id}' """
        cursor.execute(sql_statement)

# 5. 提交更新并关闭连接
conn.commit()
cursor.close()
conn.close()

print('数据更新已完成!')