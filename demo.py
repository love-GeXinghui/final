import datetime
import sys
import time
import logging

import xlsxwriter as xw
from PyQt5.QtChart import QLineSeries
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QTextCursor

from objdetector import Detector
sys.path.append("/path/to/D:/cuda/bishe/yolov5-deepsort/deep_sort/deep_sort")
from deep_sort.deep_sort import deep_sort
from deep_sort.deep_sort.deep import gol
import imutils
import cv2
import ui_login
import ui_test
import ui_register
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pymysql

#logname = str(time.asctime(time.localtime(time.time()))+".log")
#print(logname)
#logging.basicConfig(filename="example", level=logging.DEBUG)

#日志写入程序
logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter( '%(asctime)s | %(levelname)s -> %(message)s' )
file_handler=logging.FileHandler('mylogfile.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

#页面跳转
register_to_login = 0
login_to_main = 0
class test_ui(QMainWindow, ui_test.Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.show_viedo)
        self.pushButton.clicked.connect(self.video_button)
        self.pushButton_2.clicked.connect(self.select_video)
        self.pushButton_3.clicked.connect(self.warningHuman)
        self.cap_video=0
        self.flag = 0
        self.largest = 0
        self.img = []
        self.func_status = {}
        self.func_status['headpose'] = None
        self.det = Detector()
        self.judge = 0
        self.human = 0
        self.seriesArray = [0] * 100
        self.series = QLineSeries()
        for i in range(100):
            self.series.append(QPointF(i, 0))

        self.series = QLineSeries()
        self.series.setName("近期人数折线图")
        self.graphicsView.chart().addSeries(self.series)
        self.graphicsView.chart().createDefaultAxes()
        self.graphicsView.chart().axisY().setMax(1)
        self.graphicsView.chart().axisY().setMin(0)

    #选择视频
    def select_video(self):


        # 当窗口非继承QtWidgets.QDialog时，self可替换成 None
        if (self.flag == 0):
            fileName1, filetype = QFileDialog.getOpenFileName(self, "选取文件", "./",
                                                              "All Files (*);;Excel Files (*.xls)")  # 设置文件扩展名过滤,注意用双分号间隔
            self.cap_video = cv2.VideoCapture(fileName1)
            self.timer.start(50);
            self.flag += 1
            self.pushButton_2.setText("停止视频播放")
        else:
            self.timer.stop()
            self.cap_video.release()
            self.label.clear()
            self.pushButton_2.setText("开始视频播放")
            self.flag = 0

    # 选择摄像头并调用
    def video_button(self):
        if (self.flag == 0):
            self.cap_video = cv2.VideoCapture(0)
            self.timer.start(50);
            self.flag+=1
            self.pushButton.setText("关闭摄像头实时播放")
        else:
            self.timer.stop()
            self.cap_video.release()
            self.label.clear()
            self.pushButton.setText("实时视频显示")
            self.flag=0

    def show_viedo(self):
        #无法更新
        #print(global_variable)
        ret, self.img = self.cap_video.read()
        if ret:
            self.show_cv_img(self.img)

    def show_cv_img(self, img):

        self.img = self.det.feedCap(self.img, self.func_status)
        #调用全局变量来获得当前检测人数
        self.num = gol.get_value('a')
        #显示当前人数
        self.lcdNumber.display(self.num)
        if self.judge == 1:
            print(0)
            if self.num >= self.human:
                print(1)

                self.judge = 0
                ts = str(time.asctime(time.localtime(time.time())))
                nh = "当前人数为"+str(self.num)+"超过预先预警人数"
                print(time.asctime(time.localtime(time.time())))
                QMessageBox.warning(self, ts, nh, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        #显示控制台结果
        self.textEdit.append("{}   ---   {}人".format(time.asctime(time.localtime(time.time())), self.num))
        self.textEdit.moveCursor(QTextCursor.End)
        if self.largest < self.num:
            self.largest = self.num
        #显示最大人数
        self.lcdNumber_2.display(self.largest)
        self.img = self.img['frame']
        self.img = imutils.resize(self.img, height=500)
        #画图
        self.seriesArray.pop(0)
        self.seriesArray.append(self.num)
        self.series.replace([QPointF(i, self.seriesArray[i]) for i in range(100)])
        self.graphicsView.chart().axisX().setMax(100)
        if max(self.seriesArray) > 0:
            self.graphicsView.chart().axisY().setMax(max(self.seriesArray))
        #显示每帧图像
        shrink = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        QtImg = QtGui.QImage(shrink.data,
                             shrink.shape[1],
                             shrink.shape[0],
                             shrink.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        jpg_out = QtGui.QPixmap(QtImg).scaled(
            self.label.width(), self.label.height())

        self.label.setPixmap(jpg_out)

    def warningHuman(self):
        num = self.lineEdit.text()
        self.human = int(num)
        self.judge = 1


class login_ui(QMainWindow, ui_login.Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.check)
        self.pushButton_2.clicked.connect(self.registerUser)

    def registerUser(self):
        register_window.show()
        login_window.close()


    def check(self):
        #获取用户输入信息

        a = self.lineEdit.text()
        b = self.lineEdit_2.text()
        #数据库连接
        db = pymysql.connect(host='localhost',port=3306,user='root',password='11111111',db='bishe')
        cursor = db.cursor()
        sql = 'select * from username'
        cursor.execute(sql)
        result = cursor.fetchall()
        result = [dict(zip([k[0] for k in cursor.description],row)) for row in result]

        ulist = []
        plist = []

        for item in result:
            #item内部参数为表的名字
            ulist.append(item['user'])
            plist.append(item['password'])

        for i in range(len(ulist)):
            if a == ulist[i] and b == plist[i]:
                QMessageBox.information(self, "登录信息", "登陆成功", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                tempLogInString = "user:"+a +" password "+b
                logger.info(tempLogInString)
                main_window.show()
                login_window.close()
                login_to_main = 0
                break
            else:
                login_to_main = 1


        if login_to_main==1:
            QMessageBox.warning(self, "登录信息", "用户名或密码错误", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

class register_ui(QMainWindow, ui_register.Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.register)

    def register(self):
        # 获取用户输入信息
        #用户名
        a = self.lineEdit_3.text()
        #密码
        b = self.lineEdit.text()
        #确认密码
        c = self.lineEdit_2.text()

        # 数据库连接

        try:

            if a == '' or b == '':

                QMessageBox.warning(self, "注册信息", "用户名或密码不能为空", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            elif  b != c:
                QMessageBox.warning(self, "注册信息", "两次输入密码不同", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            else:
                db = pymysql.connect(host='localhost', port=3306, user='root', password='11111111', db='bishe')
                cursor = db.cursor()
                sql = 'select * from username'
                cursor.execute(sql)
                result = cursor.fetchall()
                print(0)
                result = [dict(zip([k[0] for k in cursor.description], row)) for row in result]

                ulist = []
                print(1)
                for item in result:
                    print(2)
                    ulist.append(item['user'])

                print(3)
                # sql = 'INSERT INTO 登陆账户(用户名,密码) VALUES(%s,%s)'
                cursor = db.cursor()
                print(4)
                cursor.execute('INSERT INTO username(user,password) VALUES(%s,%s)', (a, b))
                print(5)
                if a in ulist:
                    QMessageBox.warning(self, "注册信息", "用户名已存在", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    cursor.close()
                    db.close()
                    db.rollback()
                    register_window.close()
                    print("here")
                    register_window.show()
                else:
                    # 提交事务
                    db.commit()
                    QMessageBox.information(self, "注册信息", "恭喜您注册成功", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    register_to_login = 1

                cursor.close()
                db.close()
                register_window.close()
                login_window.show()


        except:
            register_window.close()
            print("here")
            register_window.show()












if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = test_ui()
    login_window = login_ui()
    register_window = register_ui()
    login_window.show()
    #main_window.show()


    sys.exit(app.exec_())
