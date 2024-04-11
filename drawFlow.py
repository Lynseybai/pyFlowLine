'''
此模块负责画流量图,版本已经更新到：不需要json控制画图
'''
import pandas as pd
import datetime 
from pyecharts import options as opts
from pyecharts.charts import Line,Page
from . import common
from . import trend

class DrawFlow():
    def __init__(self,project_name ,html):
        self.project_name = project_name
        self.html = html

    def cfg_dict(self,id_list):            
        '''
        给需要画的图生成位置，每个店铺都有必须要画的五个图，分别是
        实收 income系列，
        单量 order系列，
        客单价 atp系列 （Average Transaction Price）
        曝光 exposure系列，
        点击率 ctr系列
        最后给项目整体的神抢手生成一个图片：sqs
        '''   
        position = []
        if self.project_name == '暴暴锅':
            startTop = 25*(trend.Trend().table()[1]+1)
            print(f'暴暴锅：{startTop}')
        else:
            startTop = 30
        for item in range(0,id_list):
            top_ = startTop+item*420

            income_posi = dict(cid = 'income%s' % item, width = '600px', height = '400px',
                        top = '%spx' % top_, left = '8px')

            order_posi = dict(cid = 'order%s' % item, width = '600px', height = '400px',
                        top = '%spx' % top_, left = '640px')

            atp_posi = dict(cid = 'atp%s' % item, width = '600px', height = '400px',
                        top = '%spx' % top_, left = '1280px')

            exposure_posi = dict(cid = 'exposure%s' % item, width = '600px', height = '400px',
                        top = '%spx' % top_, left = '1920px')

            ctr_posi = dict(cid = 'ctr%s' % item, width = '600px', height = '400px',
                        top = '%spx' % top_, left = '2560px')

            position.extend([income_posi,order_posi,atp_posi,exposure_posi,ctr_posi])

        top_ = startTop+id_list*420
        sqs_posi = dict(cid = 'sqs', width = '600px', height = '400px',
                         top = '%spx' % top_, left = '8px')
        position.append(sqs_posi)
        return position 

    # 画图函数，income_mt是美团实收和曝光人数，负责前三图和第四图的商圈数据部分；
    # income_elm是饿了么实收数据，负责前三图的饿了么部分；
    # flow_df是流量数据，负责第四个和第五个图
    def line_draw(self, income_mt, income_elm, flow_df, shenqiangshou):

        # 生成page页面
        page = Page(layout= Page.DraggablePageLayout,page_title='%s%s'% (common.Common().time_node(1),self.project_name))

        # 调用trend模块，将生成的结论放入网站，目前只支持暴暴锅项目(拼好饭的数据其他项目不准orz)
        if self.project_name == '暴暴锅':
            conclusion = trend.Trend()
            page.add(conclusion.table()[0])

        # 获取要画图的店铺id列表
        id_list = flow_df['店铺名称'].unique().tolist()
        
        # 开始画图，每个店铺有三张图，一张实收和拼好饭实收，一张流量（推广，自然，拼好饭）曝光次数，一张和流量有关的进店率图，进店率 = 进店次数/曝光次数
        for i in range(len(id_list)):

            income_line_mt = income_mt.loc[income_mt['店铺名称']==id_list[i],:]
            income_line_elm = income_elm.loc[income_elm['店铺名称']==id_list[i],:]
            flow_line = flow_df.loc[flow_df['店铺名称']==id_list[i],:]
            # 实收的图
            line1 = Line(init_opts=opts.InitOpts(chart_id='income%s' % i))\
                .add_xaxis(income_line_mt['日期'].apply(lambda x:x.strftime('%m-%d')).tolist())\
                .add_yaxis("美团实收",income_line_mt['商家实收'], color='#FFA500')\
                .add_yaxis("拼好饭实收",income_line_mt['拼好饭实收'], color='#228B22')\
                .add_yaxis("美团主站实收", income_line_mt['主站实收'], color='#9400D3')\
                .add_yaxis("饿了么实收",income_line_elm['商家实收'], color='#4876FF')\
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),\
                            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max",name="最大值"),  \
                            opts.MarkPointItem(type_="min",name="最小值")],symbol='pin') ) \
                .set_global_opts(title_opts=opts.TitleOpts(title=income_line_mt['店铺名称'].tolist()[0], subtitle="%s 实收数据" % common.Common().time_node(1) ),\
                toolbox_opts=opts.ToolboxOpts(),\
                datazoom_opts=opts.DataZoomOpts(is_show=True,range_start=0,range_end=100,orient='horizontal'))    

            # 单量的图
            line2 = Line(init_opts=opts.InitOpts(chart_id='order%s' % i))\
                .add_xaxis(income_line_mt['日期'].apply(lambda x:x.strftime('%m-%d')).tolist())\
                .add_yaxis("美团单量", income_line_mt['有效单量'], color='#FFA500')\
                .add_yaxis("主站单量", income_line_mt['主站单量'], color='#9400D3')\
                .add_yaxis("拼好饭单量", income_line_mt['拼好饭单量'], color='#228B22')\
                .add_yaxis("饿了么单量",income_line_elm['有效单量'], color='#4876FF')\
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),\
                            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max",name="最大值"),  \
                            opts.MarkPointItem(type_="min",name="最小值")],symbol='pin') )\
                .set_global_opts(title_opts=opts.TitleOpts(title=income_line_mt['店铺名称'].tolist()[0], subtitle="%s 订单数" % common.Common().time_node(1) ),\
                toolbox_opts=opts.ToolboxOpts(),\
                datazoom_opts=opts.DataZoomOpts(is_show=True,range_start=0,range_end=100,orient='horizontal')) 

            #客单价的图
            line3 = Line(init_opts=opts.InitOpts(chart_id='atp%s' % i))\
                .add_xaxis(income_line_mt['日期'].apply(lambda x:x.strftime('%m-%d')).tolist())\
                .add_yaxis("美团客单", income_line_mt['美团客单'], color='#FFA500')\
                .add_yaxis("主站客单", income_line_mt['主站客单'], color='#9400D3')\
                .add_yaxis("拼好饭客单", income_line_mt['拼好饭客单'], color='#228B22')\
                .add_yaxis("饿了么客单",income_line_elm['饿了么客单'], color='#4876FF')\
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),\
                            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max",name="最大值"),  \
                            opts.MarkPointItem(type_="min",name="最小值")],symbol='pin') )\
                .set_global_opts(title_opts=opts.TitleOpts(title=income_line_mt['店铺名称'].tolist()[0], subtitle="%s 客单" % common.Common().time_node(1) ),\
                toolbox_opts=opts.ToolboxOpts(),\
                datazoom_opts=opts.DataZoomOpts(is_show=True,range_start=0,range_end=100,orient='horizontal')) 

            # 流量的图
            line4 = Line(init_opts=opts.InitOpts(chart_id='exposure%s' % i))\
                .add_xaxis(flow_line['日期'].apply(lambda x:x.strftime('%m-%d')).tolist())\
                .add_yaxis("推广次数", flow_line['推广流量'], color='#CD2626')\
                .add_yaxis("自然次数", flow_line['自然流量'], color='#9400D3')\
                .add_yaxis("拼好饭次数", flow_line['拼好饭流量'], color='#228B22')\
                .add_yaxis('前10曝光人数',income_line_mt['曝光人数同行'], color='#4682B4')\
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),\
                            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max",name="最大值"),  \
                            opts.MarkPointItem(type_="min",name="最小值")],symbol='pin') )\
                .set_global_opts(title_opts=opts.TitleOpts(title=flow_line['店铺名称'].tolist()[0], subtitle="%s 流量数据" % common.Common().time_node(1) ),\
                toolbox_opts=opts.ToolboxOpts(),\
                datazoom_opts=opts.DataZoomOpts(is_show=True,range_start=0,range_end=100,orient='horizontal')) 

            # 进店率的图
            line5 = Line(init_opts=opts.InitOpts(chart_id='ctr%s' % i))\
                .add_xaxis(flow_line['日期'].apply(lambda x:x.strftime('%m-%d')).tolist())\
                .add_yaxis("推广进店率", flow_line['推广进店率'], color='#CD2626')\
                .add_yaxis("自然进店率", flow_line['自然进店率'], color='#9400D3')\
                .add_yaxis("拼好饭进店率", flow_line['拼好饭进店率'], color='#228B22')\
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),\
                                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max",name="最大值"),  \
                                opts.MarkPointItem(type_="min",name="最小值")],symbol='pin') ) \
                .set_global_opts(title_opts=opts.TitleOpts(title=flow_line['店铺名称'].tolist()[0], subtitle="%s 进店率数据" % common.Common().time_node(1) ),\
                toolbox_opts=opts.ToolboxOpts(),\
                datazoom_opts=opts.DataZoomOpts(is_show=True,range_start=0,range_end=100,orient='horizontal')) 
            # print('这一次画图的店铺是{}'.format(flow_line['店铺名称'].unique()))
            
            page.add(line1,line2,line3,line4,line5)   

        # 神抢手的图
        line6 = Line(init_opts=opts.InitOpts(chart_id='sqs' ))\
                .add_xaxis(shenqiangshou['日期'].apply(lambda x:x.strftime('%m-%d')).tolist())  \
                .add_yaxis("券包售卖数量", shenqiangshou['券数量'], color='#CD2626') \
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),\
                                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max",name="最大值"),  \
                                opts.MarkPointItem(type_="min",name="最小值")],symbol='pin') ) \
                .set_global_opts(title_opts=opts.TitleOpts(title='%s神抢手售卖数据'% self.project_name, subtitle="%s" % common.Common().time_node(1) ),\
                toolbox_opts=opts.ToolboxOpts(),\
                datazoom_opts=opts.DataZoomOpts(is_show=True,range_start=0,range_end=100,orient='horizontal')) 
        page.add(line6)

        page.render('test.html')

        id_list_len = len(id_list)

        position = self.cfg_dict(id_list_len)

        Page.save_resize_html("test.html",   # 上面的HTML文件名称
                        cfg_dict=position,
                        dest="%s" % self.html)  # 新的文件名称 
        print('%s 的图已经画完！' % self.project_name)

    def draw_(self):
        # 设置参数，获取30日，暴暴锅项目的数据
        time_ = common.Common().time_node(30)
        project_name = self.project_name

        #获取美团的每日实收数据
        read_sql = " select t2.所属项目 项目, t1.平台店铺id 门店ID, t2.店铺名称, t1.日期, \
            t1.商家实收, t1.有效单量, ifnull(Round(t1.商家实收/t1.有效单量,1),0) as 美团客单,\
            t1.商家实收-t1.`拼好饭-收入` as 主站实收, \
            t1.有效单量-t1.`拼好饭-订单` as 主站单量, \
            ifnull(Round((t1.商家实收-t1.`拼好饭-收入`)/(t1.有效单量-t1.`拼好饭-订单`),1),0) as 主站客单, \
            t1.`拼好饭-收入` as 拼好饭实收, t1.`拼好饭-订单` 拼好饭单量,\
            ifnull(Round(t1.`拼好饭-收入`/t1.`拼好饭-订单`,1),0)  as 拼好饭客单, \
            t1.曝光人数_商家 曝光人数, t1.`曝光人数_同行前10%%%%均值` 曝光人数同行 \
            from every_day t1 \
            left join kitchen_id t2 \
            on t1.平台店铺id = t2.美团店铺id \
            where t2.所属项目 = '%s' \
            and t1.日期>= '%s'\
            and t2.是否画图 = '是' \
            order by t1.日期;" % (project_name,time_)
        
        income_mt = common.Common().df_from_sql(read_sql).round({'商家实收':0,'拼好饭实收':0,'主站实收':0})

        #获取饿了么的每日实收数据
        read_sql = " select t1.平台店铺id 门店ID, t2.店铺名称, t1.日期,\
            t1.商家实收, t1.有效单量, Round(t1.商家实收/t1.有效单量,1) as 饿了么客单\
            from daily_elm t1\
            left join kitchen_id t2\
            on t1.平台店铺id = t2.饿了么店铺id \
            where t2.所属项目 = '%s' \
            and t1.日期>= '%s'\
            and t2.是否画图 = '是' \
            order by t1.日期;" % (project_name,time_)

        income_elm = common.Common().df_from_sql(read_sql).round({'商家实收':0})

        # 获取流量、进店率数据
        read_sql = "select t4.所属项目, t3.日期, t3.门店ID, t4.店铺名称,\
            sum(case when t3.分类='推广流量' then t3.曝光次数 else 0 end) 推广流量,\
            sum(case when t3.分类='自然流量' then t3.曝光次数 else 0 end) 自然流量,\
            sum(case when t3.分类='拼好饭流量' then t3.曝光次数 else 0 end) 拼好饭流量,\
            Round(sum(case when t3.分类='推广流量' then t3.进店次数 else 0 end)*100/sum(case when t3.分类='推广流量' then t3.曝光次数 else 0 end),1) 推广进店率,\
            Round(sum(case when t3.分类='自然流量' then t3.进店次数 else 0 end)*100/sum(case when t3.分类='自然流量' then t3.曝光次数 else 0 end),1) 自然进店率,\
            Round(sum(case when t3.分类='拼好饭流量' then t3.进店次数 else 0 end)*100/sum(case when t3.分类='拼好饭流量' then t3.曝光次数 else 0 end),1) 拼好饭进店率\
            from (\
            select t1.门店ID, t1.日期, t2.分类,\
            sum(t1.曝光次数) 曝光次数 ,\
            sum(t1.进店次数) 进店次数\
            from promotion_flow t1\
            left join flow_map t2\
            on t1.分类 = t2.渠道\
            where t1.日期>= '%s' \
            group by t1.日期, t1.门店ID, t2.分类) t3\
            left join kitchen_id t4\
            on t3.门店ID = t4.美团店铺id \
            where t4.所属项目= '%s'\
            and t4.是否画图 = '是' \
            group by t3.日期, t3.门店ID, t4.店铺名称,t4.所属项目\
            order by 日期;\
        " % (time_,project_name)
        
        flow_df = common.Common().df_from_sql(read_sql)

        # 神抢手数据读取
        read_sql=" select 日期, 品牌名称, 券包售卖数量 券数量, Round(券包售卖顾客实付,0) 顾客实付\
        from shenqiangshou\
        where 日期>= '%s' \
        and 品牌名称 = '%s';" % (time_,project_name)

        shenqiangshou = common.Common().df_from_sql(read_sql)

        self.line_draw(income_mt, income_elm, flow_df, shenqiangshou)