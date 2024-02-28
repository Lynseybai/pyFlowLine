'''
负责存入数据的module，方便重新写入数据覆盖数据
'''
import pandas as pd
from . import common
from sqlalchemy import create_engine, text

class DataToMysql(object):
    
    def __init__(self,kitchen_id='平台店铺id'):
        # self.filename = filename
        # self.table_name = table_name
        self.kitchen_id = kitchen_id

    # 创建数据表，写入原始数据，并且设定主键，数据来源od
    def to_mysql(self, df, table_name):
        import datetime
        # 连接数据库
        # table_name = self.table_name
        kitchen_id = self.kitchen_id
        engine = create_engine('mysql+pymysql://root:123456@localhost:3306/every_day?charset=utf8')

        # 调用映射关系函数
        dtypedict = common.Common().mapping_df_types(df)

        # 写入数据
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False, dtype=dtypedict)

        alter_table_sql = '''
        ALTER TABLE %s
        ADD PRIMARY KEY(%s,日期)
        ''' % (table_name,kitchen_id)
        engine.connect().execute(text(alter_table_sql))
        engine.connect().close()

        print(f'{datetime.date.today()}:{table_name}数据已写入！')

    # 写入美团数据
    # filename = '美团数据.xls'
    def mtDataSql(self, filename = '美团数据.xls'):
        # filename = '美团数据.xls'
        # filename = self.filename
        
         # 将所有数据导入数据库
        df= pd.read_excel(filename,header = [0,1])

        # 数据处理
        df.columns = [common.Common().format_column_name(col) for col in df.columns]
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        list_str_float = ['到店转化率_商家', '到店转化率_同行均值', '到店转化率_同行前10%均值', '下单转化率_商家', '下单转化率_同行均值', '下单转化率_同行前10%均值',
                        '近7日复购率', '近30日复购率', '新客进店转化率', '新客下单转化率', '老客进店转化率', '老客下单转化率', '7日出餐真实上报率','出餐超时率']
        df[list_str_float] = df[list_str_float].apply(common.Common().str_float)
        self.to_mysql(df, 'every_day')


    # 写入饿了么数据
    # filename = '饿了么数据.xls'
    def elm_data(self, filename = '饿了么数据.xls'):
        # filename = '饿了么数据.xls'
        # filename = self.filename
        df = pd.read_excel(filename,header=[0,1])
        df.columns = [common.Common().format_column_name(col) for col in df.columns]
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        list_str_float = ['到店转化率_商家', '到店转化率_同行均值', '到店转化率_同行前10%均值', '下单转化率_商家', '下单转化率_同行均值', '下单转化率_同行前10%均值',
                        '近7日复购率', '近30日复购率', '新客进店转化率', '新客下单转化率', '老客进店转化率', '老客下单转化率','出餐超时率']
        df[list_str_float] = df[list_str_float].apply(common.Common().str_float)
        self.to_mysql(df, 'daily_elm')


    # 存入店铺id表
    # filename = '店铺id表.xlsx'
    def mapping_kitchen_id(self, filename = '店铺id表.xlsx'):
        # filename = '店铺id表.xlsx'
        # filename = self.filename
        data = pd.read_excel(filename)
        engine = create_engine('mysql+pymysql://root:123456@localhost:3306/every_day?charset=utf8')
        engine.connect()
        data.to_sql(name='kitchen_id', con=engine, if_exists='replace', index=False)
        engine.connect().close()
        print("店铺id表已更新！")

    # 存入流量对应表
    def flow_matching(self, filename = '流量对应表.xlsx'):

        data = pd.read_excel(filename)
        engine = create_engine('mysql+pymysql://root:123456@localhost:3306/every_day?charset=utf8')
        engine.connect()
        data.to_sql(name='flow_map', con=engine, if_exists='replace', index=False)
        engine.connect().close()
        print("流量对应表已更新！")

    # filename = 'cdpy流量明细.xlsx'
    def flow_read(self, filename = 'cdpy流量明细.xlsx'):
        # filename = 'cdpy流量明细.xlsx'
        # filename = self.filename 
        df = pd.read_excel(filename)
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        df = df.loc[df['类型']!='整体',:]

        engine = create_engine('mysql+pymysql://root:123456@localhost:3306/every_day?charset=utf8')

        dtypedict = common.Common().mapping_df_types(df)

        df.to_sql(name='promotion_flow', con=engine, if_exists='replace', index=False, dtype=dtypedict)

        alter_table_sql = '''
        ALTER TABLE promotion_flow
        ADD PRIMARY KEY(门店id,日期,分类)
        '''
        engine.connect().execute(text(alter_table_sql))
        engine.connect().close()
        
        print('流量数据已经存入数据库！')

