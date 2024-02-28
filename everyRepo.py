#更新每日数据
import xlwings as xw
import os

app = xw.App()
wb1 = app.books.open('D:/周月日报test/日报模板.xlsx') #打开excel文件

filelist = os.listdir('D:/周月日报test/源数据')
for filename in filelist:
    if filename.split('_')[1] == '美团':
        sht1 = wb1.sheets['数据'] 

    elif filename.split('_')[1] == '饿了么':
        sht1 = wb1.sheets['饿了么数据']
        
    wb2 = app.books.open('D:/周月日报test/源数据/'+filename)#打开每天下载的数据
    info = sht1.used_range
    rows = info.last_cell.row
    cols = info.last_cell.column
    sht2 = wb2.sheets[0]
    info_sht = sht2.used_range
    rows_sht = info_sht.last_cell.row
    my_values = sht2.range('a3:bh'+str(rows_sht)).options(ndim=2).value
    sht1.range('b'+str(rows+1)).value = my_values
    source_range = sht1.range('a260:a'+str(rows)).api
    info = sht1.used_range
    rows = info.last_cell.row
    cols = info.last_cell.column
    fill_range = sht1.range('a260:a'+str(rows)).api
    source_range.AutoFill(fill_range,0)
    wb2.close()

print('数据已写入日报数据库！')