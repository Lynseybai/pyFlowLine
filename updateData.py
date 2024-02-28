'''
此文件为更新每日数据的模块，负责更新数据并且检测数据完整性
'''
from tokenize import Ignore
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
import datetime
from . import common

class UpdateData():
    def __init__(self,filepath='数据更新文件'):
        self.filepath = filepath
        self.log = ''

    # 读取日常需要更新的数据,数据源是OD的；
    def data_update_od(self, df):
        # 应用函数来格式化列名
        df.columns = [common.Common().format_column_name(col) for col in df.columns]

        #判断数据是否完整
        if (df['商家实收']==0).sum()>0:
            # print('{}数据异常！请检查是否绑定账号！'.format(df['店铺'].loc[df['商家实收']==0]))
            # '%s 美团无实收数据，请检查是否绑定账号！\n'.join(self.log) % df['店铺'].loc[df['商家实收']==0]
            self.log = self.log+'%s 美团无实收数据，请检查是否绑定账号！\n' % df['店铺'].loc[df['商家实收']==0].values
        if (df['曝光人数_商家']==0).sum()>5:
            print('转化率数据未跑出！请等待美团后台的数据！')
            self.log = self.log+'转化率数据未跑出！请等待美团后台的数据！\n'
            #'转化率数据未跑出！请等待美团后台的数据！\n'.join(self.log)

        # 数据处理
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        list_str_float = ['到店转化率_商家', '到店转化率_同行均值', '到店转化率_同行前10%均值', '下单转化率_商家', '下单转化率_同行均值', '下单转化率_同行前10%均值',
                        '近7日复购率', '近30日复购率', '新客进店转化率', '新客下单转化率', '老客进店转化率', '老客下单转化率', '7日出餐真实上报率','出餐超时率']
        df[list_str_float] = df[list_str_float].apply(common.Common().str_float)
        return df

    def data_update_elm(self, df):
        # 应用函数来格式化列名
        df.columns = [common.Common().format_column_name(col) for col in df.columns]

        #判断数据是否完整
        if (df['商家实收']==0).sum()>0:
            # print('{}数据异常！请检查是否绑定账号！'.format(df['店铺'].loc[df['商家实收']==0]))
            self.log = self.log+'%s 饿了么无实收数据，请检查是否绑定账号！\n' % df['店铺'].loc[df['商家实收']==0].values

        # 数据处理
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        list_str_float = ['到店转化率_商家', '到店转化率_同行均值', '到店转化率_同行前10%均值', '下单转化率_商家', '下单转化率_同行均值', '下单转化率_同行前10%均值',
                        '近7日复购率', '近30日复购率', '新客进店转化率', '新客下单转化率', '老客进店转化率', '老客下单转化率','出餐超时率']
        df[list_str_float] = df[list_str_float].apply(common.Common().str_float)
        return df

    # 对更新的流量数据进行处理
    def data_update_flow(self, df):
        # df.ffill(axis=0,inplace=True)
        # data = pd.read_excel('店铺id表.xlsx')
        # df = pd.merge(df,data,left_on='店铺名',right_on='流量_店铺名称')
        df = df.loc[df['类型']!='整体',['美团平台店铺id','店铺名','日期','类型','分类','曝光次数','进店次数']]
        # if df.values == None:
        #     '美团流量数据未跑出！请11点重试！\n'.join(self.log)
        df.rename(columns={'美团平台店铺id':'门店ID'},inplace=True)
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        #df.to_csv('to.csv',encoding='utf_8_sig')
        return df

    # 将更新数据写入数据库进行更新
    def data_update_to_sql(self,df,table_name,table_name_temp,primary):
        engine = create_engine('mysql+pymysql://root:123456@localhost:3306/every_day?charset=utf8')

        # 调用映射关系函数
        dtypedict = common.Common().mapping_df_types(df)
        df.to_sql(name=table_name_temp, con=engine, if_exists='replace', index=False, dtype=dtypedict)
        conn = engine.connect()
        transaction = conn.begin()

        # 设置主键并且运行更新数据库的指令     
        conn.execute(text("ALTER TABLE %s ADD PRIMARY KEY(%s日期)" % (table_name_temp,primary)))

        conn.execute(text("REPLACE INTO %s SELECT * FROM %s" % (table_name,table_name_temp)))

        transaction.commit()
        conn.close()

    # 更新数据，分为，分日期美团。分日期饿了么。流量数据。神抢手数据四个部分
    def data_update(self):
        import os
 
        # current_work_dir = os.path.dirname(__file__)  # 当前文件所在的目录
        # print(current_work_dir)
        filepath = self.filepath
        # print('./'+filepath)
        # str1 = current_work_dir+'/'+filepath
        # str1.replace('\','/')
        filelist = os.listdir('./'+filepath)
        file_temp = []
        for i in filelist:
            fn_l = i.split('_')
            if (fn_l[0] == '分日期') & (fn_l[1] == '美团'):
                df = pd.read_excel(filepath + '/' + i, header=[0,1])

                #数据处理
                df = self.data_update_od(df)
                #写入mysql
                self.data_update_to_sql(df,'every_day','temp_test','平台店铺id,')
                file_temp.append(['美团实收'])

            elif fn_l[0] == '综合数据':
                day1, day2 = fn_l[2],fn_l[3].split('(')[0]
                # print('第一个日期：{}，第二个日期：{}'.format(day1,day2))

                if day1 == day2:
                    df = pd.read_excel(filepath + '/' + i, header=1,sheet_name='美团流量明细')
                    # temp = list(df.keys())[0]
                    # print(temp)
                    # print(temp=='美团流量明细')

                    # if temp == '美团流量明细':
                    df['日期'] = fn_l[2]
                    df.ffill(axis=0,inplace=True)
                    # else :
                    #     self.log = self.log+'美团流量文件下载出错！请选择综合数据-美团-展开自定义-美团流量明细'
                    #     print('美团流量文件下载出错！请选择综合数据-美团-展开自定义-美团流量明细')
                    #     self.writeLog()
                    #     return 

                    # # 数据处理
                    # df = data_update_flow(df)
                    # df.to_csv('to.csv',encoding='utf_8_sig')
                    # # 写入mysql
                    # data_update_to_sql(df,'promotion_flow','temp_test_flow','门店ID,分类,')
                else  :
                    xls = pd.ExcelFile(filepath + '/' + i)
                    df = pd.DataFrame()
                    day2 = datetime.datetime.strptime(day2, "%Y-%m-%d").date()
                    day1 = datetime.datetime.strptime(day1, "%Y-%m-%d").date()
                    # print(day2)
                    # print((day2-day1).days)
                    # print(len(xls.sheet_names))
                    if (day2-day1).days == len(xls.sheet_names)-1:
                        for name in xls.sheet_names:
                            data = pd.ExcelFile.parse(xls,sheet_name=name,header=1)
                            #if data.values
                            data.ffill(axis=0,inplace=True)
                            data['日期'] = name.split('美')[0]
                            df = df._append(data)
                    # float转int
                    else :
                        print('文件下载出错！请选择综合统计-美团-日期/分日期！')
                        self.log = self.log+'文件下载出错！请选择综合统计-美团-日期/分日期！'
                        self.writeLog()
                        return
                df['美团平台店铺id'] = df['美团平台店铺id'].astype(int)
                #数据处理
                df = self.data_update_flow(df)
                # 写入数据库
                self.data_update_to_sql(df,'promotion_flow','temp_test_flow','门店ID,分类,')
                file_temp.append(['美团流量'])
        
                
            elif (fn_l[0] == '分日期') & (fn_l[1] == '饿了么'):
                df = pd.read_excel(filepath + '/' + i, header=[0,1])
                #数据处理
                df = self.data_update_elm(df)
                #写入mysql
                self.data_update_to_sql(df,'daily_elm','temp_test_elm','平台店铺id,')
                file_temp.append(['饿了么实收'])

            elif fn_l[0] == '神抢手':
                df = pd.read_csv(filepath + '/' + i, encoding='ANSI')
                df['日期'] = pd.to_datetime(pd.Series(df['日期']),format="%Y%m%d").dt.date
                # 写入mysql
                self.data_update_to_sql(df,'shenqiangshou','temp_sqs','')
                file_temp.append(['神抢手'])

            else :
                print("文件夹有异常数据！请管理员检查!")
                self.log=self.log+'文件夹有异常数据！请管理员检查!\n'
                os.startfile(filepath)

        print(f'本次已经录入的文件：{filelist}\n共{len(filelist)}个文件')
        self.log = self.log+f'本次已经录入的文件：{filelist}\n共{len(filelist)}个文件'
        self.writeLog()


    def writeLog(self):
        with open('运行结果文档.txt','w') as f:
            f.write(self.log)