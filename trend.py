from tokenize import Double
import numpy as np
import pandas as pd
from  sklearn.linear_model import LinearRegression
from . import common
# import common
from pyecharts import options as opts
from pyecharts.charts import Line,Page
from pyecharts.components import Table
'''
本文件负责数据预警模型的数据计算部分
0、实收变化趋势
1、拼好饭和主站实收的占比变化、单量的占比变化
2、UV值变化趋势
3、对数计算四个指标的贡献率
'''
class Trend():

    def __init__(self):
        pass
    
    # 拉取数据的抽象方法
    def pullData(self, time_node=8):

        time_ = common.Common().time_node(time_node)

        read_sql = " select t2.所属项目 项目, t1.平台店铺id 门店ID, t2.店铺名称, t1.日期, \
            t1.商家实收, t1.有效单量, Round(t1.商家实收/t1.有效单量,1) as 美团客单,\
            t1.商家实收-t1.`拼好饭-收入` as 主站实收, \
            t1.有效单量-t1.`拼好饭-订单` as 主站单量, \
            Round((t1.商家实收-t1.`拼好饭-收入`)/(t1.有效单量-t1.`拼好饭-订单`),1) as 主站客单, \
            t1.`拼好饭-收入` as 拼好饭实收, t1.`拼好饭-订单` 拼好饭单量,\
            Round(t1.`拼好饭-收入`/t1.`拼好饭-订单`,1)  as 拼好饭客单, \
            t1.曝光人数_商家 曝光人数, t1.`曝光人数_同行前10%%%%均值` 曝光人数同行 \
            from every_day t1 \
            left join kitchen_id t2 \
            on t1.平台店铺id = t2.美团店铺id \
            where t1.日期>= '%s'\
            and t2.是否画图 = '是' \
            and t2.所属项目 in ('暴暴锅','炊大妈') \
            order by t2.顺序;" % time_

        income_mt = common.Common().df_from_sql(read_sql).round({'商家实收':0,'拼好饭实收':0,'主站实收':0})
        return income_mt

    def temp(self):
        income_mt = self.pullData()
        id_list = income_mt['店铺名称'].unique().tolist()
        decrease_list = []
        for i in range(len(id_list)):

            x = np.array(range(8))
            y = income_mt.loc[income_mt['店铺名称']==id_list[i],'商家实收'].to_numpy()

            # 调用线性回归，计算回归系数
            if len(y) == 8:
                w0, w1 = self.linearFit(x,y)
                if w1 < 0:
                    decrease_list.append(id_list[i])
        str = '，'
        print(f'美团实收下降趋势，请及时提升：{str.join(decrease_list)}')

    # 计算一元线性回归，得到趋势
    def linearFit(self, x, y):
        model = LinearRegression()
        model.fit(x.reshape(-1, 1), y.reshape(-1,1))
        # print('{}回归截距: w0={}'.format(kitchen_name, model.intercept_))  # w0: 截距
        # print('{}回归系数: w1={}'.format(kitchen_name, model.coef_))  # w1,..wm: 回归系数
        return model.intercept_ , model.coef_

    # 双渠道（拼好饭+主站)趋势变化
    def doubleChannel(self):
        income_mt = self.pullData()
        id_list = income_mt['店铺名称'].unique().tolist()
        page = Page(layout= Page.DraggablePageLayout,page_title='%s'% common.Common().time_node(1))
        for i in id_list:
            if (i != '暴暴锅九眼桥') & (i != '梁家巷'):
                continue
            df = income_mt.loc[income_mt['店铺名称']==i,:]
            df['拼好饭实收占比'] = df['拼好饭实收']/df['商家实收']
            df['拼好饭单量占比'] = df['拼好饭单量']/df['有效单量']
            df = df.round({'拼好饭实收占比':2, '拼好饭单量占比':2})
            line1 = Line(init_opts=opts.InitOpts(chart_id='test%s' % i)) \
                    .add_xaxis(df['日期'].apply(lambda x:x.strftime('%m-%d')).tolist())\
                    .add_yaxis("拼好饭实收占比",df['拼好饭实收占比'], color='#FFA500')\
                    .add_yaxis("拼好饭单量占比",df['拼好饭单量占比'], color='#228B22')\
                    .set_global_opts(title_opts=opts.TitleOpts(title=i, subtitle="%s" % common.Common().time_node(1) ),\
                    toolbox_opts=opts.ToolboxOpts())  
            page.add(line1)
        page.render('test.html')
        print('run over!')

    # UV值的变化图表
    def trendUV(self, income_mt):

        page = Page(layout= Page.DraggablePageLayout,page_title='%sUV'% common.Common().time_node(1))
        id_list = income_mt['店铺名称'].unique().tolist()

        for i in id_list:
            if (i != '暴暴锅九眼桥') & (i != '梁家巷'):
                continue
            df = income_mt.loc[income_mt['店铺名称']==i,:]
            df['UV'] = df['商家实收']/df['曝光人数']
            df = df.round({'UV':2})

            line1 = Line(init_opts=opts.InitOpts(chart_id='test%s' % i)) \
                    .add_xaxis(df['日期'].apply(lambda x:x.strftime('%m-%d')).tolist())\
                    .add_yaxis("UV",df['UV'], color='#FFA500')\
                    .set_global_opts(title_opts=opts.TitleOpts(title=i, subtitle="%s UV" % common.Common().time_node(1) ),\
                    toolbox_opts=opts.ToolboxOpts())  
            page.add(line1)

        page.render('test.html')
        print('run over!')


    # 贡献率计算,计算是放在sql进行的
    # 这个函数返回昨日和前7天平均值的波动比对
    def contriRateAvg(self):

        project_name = '暴暴锅'

        read_sql = " select t4.店铺名称, t3.平台店铺id,  round(t3.商家实收波动,0) 商家实收波动,\
            (t3.曝光人数lnd+t3.入店率lnd+t3.下单率lnd+t3.客单价lnd) 测试,\
            round(t3.曝光人数lnd/(t3.曝光人数lnd+t3.入店率lnd+t3.下单率lnd+t3.客单价lnd),3) 曝光人数贡献率,\
            round(t3.入店率lnd/(t3.曝光人数lnd+t3.入店率lnd+t3.下单率lnd+t3.客单价lnd),3) 入店率贡献率,\
            round(t3.下单率lnd/(t3.曝光人数lnd+t3.入店率lnd+t3.下单率lnd+t3.客单价lnd),3) 下单率贡献率,\
            round(t3.客单价lnd/(t3.曝光人数lnd+t3.入店率lnd+t3.下单率lnd+t3.客单价lnd),3) 客单价贡献率\
            from (\
            select t1.平台店铺id,  \
            t2.商家实收-t1.平均商家实收 商家实收波动, \
            ln(t2.曝光人数)-ln(t1.平均曝光人数) 曝光人数lnd,  \
            ln(t2.到店率)-ln(t1.平均入店转化率) 入店率lnd,  \
            ln(t2.下单率)-ln(t1.平均下单转化率) 下单率lnd, \
            ln(t2.客单)-ln(t1.平均客单价) 客单价lnd \
            from ( \
            select 平台店铺id, \
            avg(商家实收-`拼好饭-收入`) 平均商家实收, \
            avg(曝光人数_商家-`拼好饭-曝光人数`) 平均曝光人数,  \
            sum(到店人数_商家-`拼好饭-到店人数`)/sum(曝光人数_商家-`拼好饭-曝光人数`) as 平均入店转化率,  \
            sum(下单人数_商家-`拼好饭-下单人数`)/sum(到店人数_商家-`拼好饭-到店人数`) as 平均下单转化率,  \
            sum(商家实收-`拼好饭-收入`)/sum(有效单量-`拼好饭-订单`) as 平均客单价  \
            from every_day  \
            where 日期 >= date_sub(curdate(), interval 8 day)  \
            and 日期< date_sub(curdate(), interval 1 day)  \
            group by 平台店铺id) t1 \
            left join \
            (select \
            平台店铺id, 日期, 商家实收-`拼好饭-收入` 商家实收,\
            曝光人数_商家-`拼好饭-曝光人数` 曝光人数,\
            (到店人数_商家-`拼好饭-到店人数`)/(曝光人数_商家-`拼好饭-曝光人数`) 到店率,\
            (下单人数_商家-`拼好饭-下单人数`)/(到店人数_商家-`拼好饭-到店人数`) 下单率,\
            (商家实收-`拼好饭-收入`)/(有效单量-`拼好饭-订单`) 客单\
            from every_day\
            where 日期=date_sub(curdate(), interval 1 day)) t2 \
            on t1.平台店铺id = t2.平台店铺id \
            ) t3 \
            left join kitchen_id t4 \
            on t3.平台店铺id = t4.美团店铺id \
            where t4.所属项目='%s' \
            ; " % project_name
        return read_sql

    # 计算昨日的同比和环比，四个指标的贡献率，time_填2或者8,2是同比，8是环比
    def contriRate(self, time_):

        project_name = '暴暴锅'

        read_sql = "select t3.平台店铺id, \
        t4.店铺名称, \
        t3.商家实收波动,\
        round(t3.曝光人数lnd/(t3.曝光人数lnd+t3.到店率lnd+t3.下单率lnd+t3.客单价lnd),3) 曝光人数贡献率,\
        round(t3.到店率lnd/(t3.曝光人数lnd+t3.到店率lnd+t3.下单率lnd+t3.客单价lnd),3) 入店率贡献率,\
        round(t3.下单率lnd/(t3.曝光人数lnd+t3.到店率lnd+t3.下单率lnd+t3.客单价lnd),3) 下单率贡献率,\
        round(t3.客单价lnd/(t3.曝光人数lnd+t3.到店率lnd+t3.下单率lnd+t3.客单价lnd),3) 客单价贡献率\
        from( \
        select t1.平台店铺id, round(t1.主站实收-t2.主站实收,0) 商家实收波动, \
        ln(t1.主站曝光)-ln(t2.主站曝光)  曝光人数lnd, \
        ln(t1.主站到店率)-ln(t2.主站到店率) 到店率lnd, \
        ln(t1.主站下单率)-ln(t2.主站下单率) 下单率lnd, \
        ln(t1.主站客单)-ln(t2.主站客单) 客单价lnd \
        from( \
        select 平台店铺id, 商家实收-`拼好饭-收入` 主站实收, \
        曝光人数_商家-`拼好饭-曝光人数` 主站曝光, \
        (到店人数_商家-`拼好饭-到店人数`)/(曝光人数_商家-`拼好饭-曝光人数`) 主站到店率, \
        (下单人数_商家-`拼好饭-下单人数`)/(到店人数_商家-`拼好饭-到店人数`) 主站下单率, \
        (商家实收-`拼好饭-收入`)/(有效单量-`拼好饭-订单`) 主站客单 \
        from \
        every_day \
        where 日期 = date_sub(curdate(), interval 1 day)) t1 \
        left join \
        ( \
        select 平台店铺id, 商家实收-`拼好饭-收入` 主站实收, \
        曝光人数_商家-`拼好饭-曝光人数` 主站曝光, \
        (到店人数_商家-`拼好饭-到店人数`)/(曝光人数_商家-`拼好饭-曝光人数`) 主站到店率, \
        (下单人数_商家-`拼好饭-下单人数`)/(到店人数_商家-`拼好饭-到店人数`) 主站下单率, \
        (商家实收-`拼好饭-收入`)/(有效单量-`拼好饭-订单`) 主站客单 \
        from \
        every_day \
        where 日期 = date_sub(curdate(), interval %s day)) t2 \
        on t1.平台店铺id = t2.平台店铺id \
        ) t3 \
        left join kitchen_id t4 \
        on t3.平台店铺id = t4.美团店铺id \
        where t4.所属项目 = '%s'; " % (time_, project_name)
        return read_sql

    # 贡献率的条件判断，输出结论
    def resContri(self):
        project_name = '暴暴锅'
        res = '%s：%s\n' % (common.Common().time_node(1), project_name)
        temp = ['较上个7天平均实收','同比','环比']
        temp2 = [self.contriRateAvg(),self.contriRate(2),self.contriRate(8)]
        count_row = 0
        for item, item2 in zip(temp, temp2):
            df = common.Common().df_from_sql(item2)
            # print(df)
            for row in df.itertuples():
                temp = []
                if getattr(row,'商家实收波动') < 0:
                    # print(f"{getattr(row,'店铺名称')}:{getattr(row,'曝光人数贡献率')}")
                    if getattr(row,'曝光人数贡献率') < 0:
                        temp.append('曝光人数')
                    if getattr(row,'入店率贡献率') < 0:
                        temp.append('入店率')
                    if getattr(row,'下单率贡献率') < 0:
                        temp.append('下单率')
                    if getattr(row,'客单价贡献率') < 0:
                        temp.append('客单')
                    if temp == []:
                        temp.append('曝光人数、入店率、下单率、客单')
                    res = res + f"{getattr(row,'店铺名称')}实收{item}呈现下降，影响的指标是：{'，'.join(temp)}" + '\n'
                    count_row+=1
                    # print(res)
        # print(res)
        return res, count_row


    def table(self):
        table = Table()
        # table.add(headers=[self.contributionRate()], rows=[], attributes={
        #     "align": "center",
        #     "border": False,
        #     "padding": "2px",
        #     "style": " width:1350px; height:50px; font-size:25px; color:#C0C0C0;"
        # })
        text, count_row = self.resContri()
        table.add(headers=[text], rows=[], attributes={
            "style": " width:1350px; height:30px; font-size:18px; color:grey;"
        })
        # table.render('大标题.html')
        # print('生成完毕:大标题.html')

        return table, count_row
         

if __name__ == '__main__':

    trend = Trend('暴暴锅')
    # df = trend.pullData(7)
    # trend.doubleChannel(df)
    trend.table()


