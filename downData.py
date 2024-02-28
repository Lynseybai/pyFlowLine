'''
负责下载数据的模块，可以手动和自动操作，目前采用电脑版按键精灵（bushi）
'''
import pyautogui
import time
import datetime
import webbrowser
import os
import shutil

class DownloadData(object):
    def __init__(self,downpath = 'C:/Users/LENOVOPC/Downloads/',update_path='数据更新文件/'):
        self.downpath = downpath
        self.update_path = update_path

    def download_data(self):
        '''
        使用浏览器：edge，缩放比例：76%，全屏
        '''
        import webbrowser
        # 打开页面
        webbrowser.open('https://cdpy.od888.cn/operationAndManage/operateAssistant/downloadcenterpage')
        
        time.sleep(20)

        print(f'本电脑的屏幕尺寸是{pyautogui.size()}')
        print(pyautogui.position())

        # 下载美团流量数据
        # 综合统计下载
        pyautogui.click(380,222,duration=1)
        # 点击选择美团
        pyautogui.click(511,280,duration=1)
        # 点击选择门店分类
        pyautogui.click(715,326,duration=1)
        # 点击选择直营店
        pyautogui.click(683,363,duration=1)
        pyautogui.click(726,565,duration=1)
        # 展开自定义项
        pyautogui.click(1620,379,duration=1)
        # 勾选去掉美团合计
        pyautogui.click(324,614,duration=1)
        # 勾选流量数据
        pyautogui.click(324,778,duration=1)
        # 下载文件
        pyautogui.click(1383,376,duration=1)
        time.sleep(30)
        pyautogui.click(959,113,duration=1)
        time.sleep(2)
        # 关闭excel界面
        pyautogui.hotkey('ctrl','w')

        # 下载美团实收数据
        # 点击选择分日期下载
        pyautogui.click(491,222,duration=1)
        # 点击选择美团
        pyautogui.click(511,280,duration=1)
        # 点击选择门店分类
        pyautogui.click(715,326,duration=1)
        # 点击选择直营店
        pyautogui.click(683,363,duration=1)
        pyautogui.click(726,565,duration=1)
        # 点击选择按模板下载
        pyautogui.click(1301,374,duration=1)
        pyautogui.click(1466,379,duration=1)
        # 选择模板--苏-日数据
        pyautogui.click(1468,381,duration=0.5)
        time.sleep(1)
        pyautogui.click(1468,381,duration=1)
        pyautogui.click(1468,550,duration=0.5)
        # 下载文件
        pyautogui.click(1575,382,duration=1)
        time.sleep(20)
        pyautogui.click(959,113,duration=1)
        # 文件下载好了，关闭页面
        time.sleep(3)
        pyautogui.hotkey('ctrl','w')


        #下载饿了么实收数据
        # 点击选择饿了么
        pyautogui.click(450,282,duration=1)
        # 选择模板--苏-日数据
        pyautogui.click(1468,381,duration=0.5)
        time.sleep(1)

        #pyautogui.click(1468,381,duration=1)
        pyautogui.click(1468,444,duration=0.5)
        # 下载文件
        pyautogui.click(1575,382,duration=1)
        time.sleep(20)
        pyautogui.click(959,113,duration=1)
        # 文件下载好了，关闭页面
        time.sleep(1)
        pyautogui.hotkey('ctrl','w')
        print("文件已经下载完毕！")

    def renewFile(self):
        path = 'D:/周月日报test/源数据/'
        # 删除存放文件的文件夹
        shutil.rmtree(path)
        # 新建新的存放文件的文件夹
        os.mkdir(path)

    def copyfileEveryRepo(self, filename):
        filepath = self.downpath
        update_path = 'D:/周月日报test/源数据/'
        shutil.copyfile(filepath+filename,update_path+filename)


    def copyfile(self):
        '''
        将下载好的文件复制到运行文件里，这样做主要是为了留存数据
        '''
        # filepath = 'C:/Users/LENOVOPC/Downloads/'
        # update_path = 'D:/新版日报数据库建设/OD美团数据更新/'
        import win32api,win32con

        update_path = self.update_path
        filepath = self.downpath

        # 删除存放文件的文件夹
        shutil.rmtree(update_path)
        # 新建新的存放文件的文件夹
        os.mkdir(update_path)
        # os.chmod(update_path, 0o777)

        #每天删除生成一个新的日报数据文件
        self.renewFile()

        today = datetime.date.today()
        new_files = []
        filelist = os.listdir(filepath)
        
        for item in filelist:
            # 获取每个文件修改的时间
            filetime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath+item)).date()

            # 获取修改时期为今天的文件
            if filetime >= today:
                new_files.append(item)
                shutil.copyfile(filepath+item,update_path+item)
                if item.split('_')[0] == '分日期':
                    self.copyfileEveryRepo(item)
        print('复制过去的文件有\n',new_files)
        os.system('python everyRepo.py')

        if len(new_files)==0:
            win32api.MessageBox(0,'文件数量有误！请重试！','错误',win32con.MB_OK)
            #print('文件数量有误！请重试！')
            return