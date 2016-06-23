#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author : MikeChan
# Email  : m7807031@gmail.com
# Date   : 06/21/2016

import time, sys, os, datetime, threading
import numpy as np
import matplotlib.pyplot as plt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#====== QT area ======
class Decode_GUI(QWidget):
    def __init__(self, parent = None):
        super(Decode_GUI, self).__init__(parent)

        self.INHERIT_KEY = False


        # create Layout and connection
        self.createLayout()
        self.createConnection()

        # window properties adjustment
        self.setGeometry(160,70,400,300)
        self.setWindowIcon(QIcon('icon/QIMU.png'))
        self.setWindowTitle(u"IMU 9軸解碼程式")

    def createLayout(self):
        self.fileLineEdit=QLineEdit()
        self.filepath_button=QPushButton(u"選擇檔案")
        h1 = QHBoxLayout()
        h1.addWidget(self.fileLineEdit)
        h1.addWidget(self.filepath_button)


        self.statusBrowser  = QTextBrowser()
        h2 = QHBoxLayout()
        h2.addWidget(self.statusBrowser)


        self.parseAll_button = QPushButton(u"解算 時間+9軸 資訊")
        h3 = QHBoxLayout()
        h3.addWidget(self.parseAll_button)



        self.parseTime_button = QPushButton(u"分離 時間 資訊")
        self.parseTimeDiff_button = QPushButton(u"分離 時間差 資訊")
        h4 = QHBoxLayout()
        h4.addWidget(self.parseTime_button)
        h4.addWidget(self.parseTimeDiff_button)


        # CheckBOX H6 options area =====
        h6 = QVBoxLayout()

        self.plotLabel=QLabel("@===== PLOT AREA ======@")
        self.plotLabel.setAlignment(Qt.AlignCenter)
        h6_0=QHBoxLayout()
        h6_0.addWidget(self.plotLabel)

        self.optionLabel_time = QLabel(u"時間(s)：")
        self.time_plot_check=QCheckBox(u"時間")
        self.timediff_plot_check=QCheckBox(u"時間差")
        h6_i= QHBoxLayout()
        h6_i.addWidget(self.optionLabel_time)
        h6_i.addWidget(self.time_plot_check)
        h6_i.addWidget(self.timediff_plot_check)


        self.optionLabel_acc = QLabel(u"三軸加速度( 16384 LSB/g)：")
        self.ax_plot_check=QCheckBox("ax")
        self.ay_plot_check=QCheckBox("ay")
        self.az_plot_check=QCheckBox("az")
        h6_ii= QHBoxLayout()
        h6_ii.addWidget(self.optionLabel_acc)
        h6_ii.addWidget(self.ax_plot_check)
        h6_ii.addWidget(self.ay_plot_check)
        h6_ii.addWidget(self.az_plot_check)

        self.optionLabel_gyro = QLabel(u"三軸角速度( 131 LSB/deg)：")
        self.gx_plot_check=QCheckBox("gx")
        self.gy_plot_check=QCheckBox("gy")
        self.gz_plot_check=QCheckBox("gz")
        h6_iii= QHBoxLayout()
        h6_iii.addWidget(self.optionLabel_gyro)
        h6_iii.addWidget(self.gx_plot_check)
        h6_iii.addWidget(self.gy_plot_check)
        h6_iii.addWidget(self.gz_plot_check)

        self.optionLabel_mag = QLabel(u"三軸磁力計(  1.6 LSB/uT )：")
        self.mx_plot_check=QCheckBox("mx")
        self.my_plot_check=QCheckBox("my")
        self.mz_plot_check=QCheckBox("mz")
        h6_iv= QHBoxLayout()
        h6_iv.addWidget(self.optionLabel_mag)
        h6_iv.addWidget(self.mx_plot_check)
        h6_iv.addWidget(self.my_plot_check)
        h6_iv.addWidget(self.mz_plot_check)

        h6.addLayout(h6_0)
        h6.addLayout(h6_i)
        h6.addLayout(h6_ii)
        h6.addLayout(h6_iii)
        h6.addLayout(h6_iv)
        # End H6

        self.toPlot_button = QPushButton(u'產出圖表')
        h7 = QHBoxLayout()
        h7.addWidget(self.toPlot_button)


        layout = QVBoxLayout()

        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addLayout(h3)
        layout.addLayout(h4)

        layout.addLayout(h6)
        layout.addLayout(h7)

        self.setLayout(layout)

    def createConnection(self):
         self.filepath_button.clicked.connect(self.openFile)
         self.parseAll_button.clicked.connect(self.parseAll)
         self.parseTime_button.clicked.connect(self.parseTime)
         self.parseTimeDiff_button.clicked.connect(self.parseTimeDiff)
         self.toPlot_button.clicked.connect(self.toPlot)

         self.parseAll_button.setEnabled(False)
         self.parseTime_button.setEnabled(False)
         self.parseTimeDiff_button.setEnabled(False)
         self.toPlot_button.setEnabled(False)

    def openFile(self):
        self.INHERIT_KEY = False

        # Choose file
        s = QFileDialog.getOpenFileName(self,u"開啟IMU檔案","/","Text files(*.txt)")
        self.fileLineEdit.setText(u'%s' %s)
        if len(self.fileLineEdit.text()) > 2:
            f = open(u'%s' %s,'r')
            first_line = f.readline().rstrip().split("\t")

            if type(first_line) == list and len(first_line) == 10:
                self.statusBrowser.append(u"解析過檔案已選擇。")
                self.parseAll_button.setEnabled(False)
                self.parseTime_button.setEnabled(True)
                self.parseTimeDiff_button.setEnabled(True)
                self.toPlot_button.setEnabled(True)

            elif type(first_line)== list and len(first_line) == 1:
                self.statusBrowser.append(u"檔案已選擇。")
                self.parseAll_button.setEnabled(True)
                self.parseTime_button.setEnabled(False)
                self.parseTimeDiff_button.setEnabled(False)
                self.toPlot_button.setEnabled(False)
            else:
                self.statusBrowser.append(u"開啟檔案錯誤! 請重新選擇。")
                self.fileLineEdit.setText("")
                self.parseAll_button.setEnabled(False)
                self.parseTime_button.setEnabled(False)
                self.parseTimeDiff_button.setEnabled(False)
                self.toPlot_button.setEnabled(False)

            f.close()
        else:
            self.statusBrowser.append(u"請重新選擇檔案。")


    def parseAll(self):
        t0= time.time()
        count = 0
        self.statusBrowser.append(u"資料解碼開始...")
        # Inner Function here =====
        def list_sep(list_1):
            j = ""
            for i in list_1:
                j += str(i) + "\t"
            return j

        def dec_2_hexdec(lst, MLSB="MSB"):
            def signed_check(num):
                if num > 32767:
                    num -= 65536
                return num

            three_num = []
            if MLSB =="MSB":
                a = lst[0]*256 + lst[1]*1
                b = lst[2]*256 + lst[3]*1
                c = lst[4]*256 + lst[5]*1

            elif MLSB =="LSB":
                a = lst[1]*256 + lst[0]*1
                b = lst[3]*256 + lst[2]*1
                c = lst[5]*256 + lst[4]*1

            three_num.append(signed_check(a))
            three_num.append(signed_check(b))
            three_num.append(signed_check(c))

            return three_num

        s = self.fileLineEdit.text()
        s1 = s[:-4]

        f = open(u"%s" %s ,"r")
        w = open(u"%s_RESULT.txt" %s1, "w")


        data_line_list = []

        # save stripped data in list
        for data_line in f.readlines():
            data_line_strip = data_line.strip()
            data_line_list.append(data_line_strip)


        for i in range(len(data_line_list)):
            if i % 4 == 0:

                axyz_list     = dec_2_hexdec(eval(data_line_list[i+1]))
                gxyz_list     = dec_2_hexdec(eval(data_line_list[i+2]))
                magxyz_list   = dec_2_hexdec(eval(data_line_list[i+3]), "LSB")
                count += 1

                #time + accer + gyro + mag
                print >> w, data_line_list[i]  + "\t" + list_sep(axyz_list)  + list_sep(gxyz_list)  +  list_sep(magxyz_list)



        f.close()
        w.close()

        self.INHERIT_KEY=True

        t1 = time.time() -t0
        self.statusBrowser.append(u"%d 筆資料解碼完成，共花費%.2f秒" %(count , t1))

        self.parseAll_button.setEnabled(True)
        self.parseTime_button.setEnabled(True)
        self.parseTimeDiff_button.setEnabled(True)
        self.toPlot_button.setEnabled(True)


    def parseTime(self):
        t0 = time.time()
        self.statusBrowser.append(u"分離資料時間...")

        time_data = []
        if self.INHERIT_KEY == False:
            s = self.fileLineEdit.text()
            f = open(u"%s" %s ,"r")
            s1 = s[:-4]
            w = open(u"%s_TIME.txt" %s1, "w")

        elif self.INHERIT_KEY == True:
            s = self.fileLineEdit.text()
            s1 = s[:-4]

            f = open(u"%s_RESULT.txt" %s1 ,"r")
            w = open(u"%s_RESULT_TIME.txt" %s1, "w")
        else:
            print "ERROR OCCUR!"


        for i in f.readlines():
            j = i.strip().split("\t")
            time_data.append(float(j[0]))

        for i in time_data:
            print >> w, i

        f.close()
        w.close()

        t1=time.time()-t0
        self.statusBrowser.append(u"時間資訊分離完成，共花費%.2f秒" %t1)
        self.toPlot_button.setEnabled(True)

    def parseTimeDiff(self):
        t0 = time.time()
        self.statusBrowser.append(u"解算資料時間差...")

        time_data = []

        if self.INHERIT_KEY == False:
            s = self.fileLineEdit.text()
            s1 = s[:-4]
            f = open(u"%s" %s ,"r")
            w = open(u"%s_TIMEDIFF.txt" %s1, "w")
        elif self.INHERIT_KEY ==True:
            s = self.fileLineEdit.text()
            s1 = s[:-4]
            f = open(u"%s_RESULT.txt" %s1 ,"r")
            w = open(u"%s_RESULT_TIMEDIFF.txt" %s1, "w")

        for i in f.readlines():
            j = i.strip().split("\t")
            time_data.append(float(j[0]))

        time_array = np.array(time_data)
        #print time_array.size
        #print type(time_array[0])

        time_diff_array = np.diff(time_array)
        #print time_diff_array.size


        mean_td = time_diff_array.mean()
        std_td = time_diff_array.std()
        max_td = np.amax(time_diff_array)
        min_td = np.amin(time_diff_array)

        data_analyst = "mean\t%f\nstd\t%f\nmax\t%f\nmin\t%f" %(mean_td, std_td, max_td, min_td)

        print >> w, "%s" %data_analyst

        for i in time_diff_array:
            print >> w, "%.6f" %i

        f.close()
        w.close()

        t1 = time.time()-t0

        self.statusBrowser.append(u"時間差資料分離完成，共花費%.2f秒" %t1)
        self.statusBrowser.append(u"時間差統計數據如下:")
        self.statusBrowser.append(u"共 %d 筆資料。" % time_diff_array.size)
        self.statusBrowser.append(u"平均值:%f    標準差:%f" %(mean_td, std_td) )
        self.statusBrowser.append(u"最大值:%f    最小值:%f" %(max_td, min_td)  )
        self.statusBrowser.append(u"========================")

        self.toPlot_button.setEnabled(True)

    def toPlot(self):

        # open right file ex. IMU_LOG_RESULT
        if self.INHERIT_KEY == False:
            s = self.fileLineEdit.text()
            f = open(u"%s" %s ,"r")

        elif self.INHERIT_KEY ==True:
            s = self.fileLineEdit.text()
            s1 = s[:-4]
            f = open(u"%s_RESULT.txt" %s1 ,"r")

        # asign value to varibles
        time=[]
        ax=[]
        ay=[]
        az=[]
        gx=[]
        gy=[]
        gz=[]
        mx=[]
        my=[]
        mz=[]


        for i in f.readlines():
            j = i.strip().split("\t")
            time.append(float(j[0]))
            ax.append(float(j[1]))
            ay.append(float(j[2]))
            az.append(float(j[3]))
            gx.append(float(j[4]))
            gy.append(float(j[5]))
            gz.append(float(j[6]))
            mx.append(float(j[7]))
            my.append(float(j[8]))
            mz.append(float(j[9]))

        self.time_array = np.array(time)
        self.time_diff_array = np.diff(self.time_array)
        self.ax_array = np.array(ax)
        self.ay_array = np.array(ay)
        self.az_array = np.array(az)
        self.gx_array = np.array(gx)
        self.gy_array = np.array(gy)
        self.gz_array = np.array(gz)
        self.mx_array = np.array(mx)
        self.my_array = np.array(my)
        self.mz_array = np.array(mz)



        #===== Plot Area =====
        #plt.plot(count_array, self.time_diff_array)

        value_list = [  self.time_array,
                        self.time_diff_array,
                        self.ax_array,
                        self.ay_array,
                        self.az_array,
                        self.gx_array,
                        self.gy_array,
                        self.gz_array,
                        self.mx_array,
                        self.my_array,
                        self.mz_array]

        checkbox_list = [   self.time_plot_check,
                            self.timediff_plot_check,
                            self.ax_plot_check,
                            self.ay_plot_check,
                            self.az_plot_check,
                            self.gx_plot_check,
                            self.gy_plot_check,
                            self.gz_plot_check,
                            self.mx_plot_check,
                            self.my_plot_check,
                            self.mz_plot_check]

        line_label = [  "time",
                        "time_diff",
                        "ax",
                        "ay",
                        "az",
                        "gx",
                        "gy",
                        "gz",
                        "mx",
                        "my",
                        "mz"]

        result = ""

        for i in range(len(checkbox_list)):
            if checkbox_list[i].isChecked():
                plt.plot(np.arange(0,value_list[i].size), value_list[i], label=line_label[i])


            else:
                pass

        plt.legend(loc='upper left')
        plt.title(result)

        plt.show()

if __name__ == "__main__":
	app=QApplication(sys.argv)
	Decode_GUI = Decode_GUI()
	Decode_GUI.show()
	sys.exit(app.exec_())
