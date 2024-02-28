'''
本文件常用的函数
'''
import datetime
import pandas as pd

class Common(object):   

    def __init__(self) -> None:
        pass

    # 将excel中的字符串转float
    def str_float(self, df):
        return df.str.strip("%").astype(float) / 100

    # 处理OD文件的多维列名
    def format_column_name(self, col):
        if "Unnamed" in col[1]:
            return col[0]
        else:
            return f"{col[0]}_{col[1]}"

    # 为df存入数据库做数据映射
    def mapping_df_types(self, df):
        from sqlalchemy.types import NVARCHAR, Float, INTEGER, DATE    
        dtypedict = {}
        for i, j in zip(df.columns, df.dtypes):
            if "object" in str(j):
                dtypedict.update({i: NVARCHAR(length=255)})
            if "float" in str(j):
                dtypedict.update({i: Float(precision=5, asdecimal=True)})
            if "int" in str(j):
                dtypedict.update({i: INTEGER()})
            if "日期" in str(i):
                dtypedict.update({i: DATE()})
        return dtypedict

    def df_from_sql(self,read_sql):
        import sqlalchemy
        engine = sqlalchemy.create_engine('mysql+pymysql://root:123456@localhost:3306/every_day?charset=utf8')
        df = pd.read_sql(read_sql,engine)
        engine.connect().close()

        return df

    def time_node(self,n):
        today = datetime.date.today()
        n_days_age = today-datetime.timedelta(days = n)
        return n_days_age