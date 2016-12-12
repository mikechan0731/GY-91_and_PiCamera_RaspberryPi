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

<<<<<<< HEAD

=======
>>>>>>> fd9988560bbd6a0c888dc87011c6b7fc72041855
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


<<<<<<< HEAD

=======
>>>>>>> fd9988560bbd6a0c888dc87011c6b7fc72041855
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

<<<<<<< HEAD
        self.optionLabel_mag = QLabel(u"三軸磁力計(  1.6 LSB/uT )：")
=======
        self.optionLabel_mag = QLabel(u"三軸磁力計( 1.6 LSB/uT )：")
>>>>>>> fd9988560bbd6a0c888dc87011c6b7fc72041855
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
<<<<<<< HEAD
        self.fileLineEdit.setText(u'%s' %s)
=======

        self.fileLineEdit.setText(s)

        #self.statusBrowser.append(u"檔案已選擇。")
        #time.sleep(0.5)


>>>>>>> fd9988560bbd6a0c888dc87011c6b7fc72041855
        if len(self.fileLineEdit.text()) > 2:
            f = open(u'%s' %s,'r')
            first_line = f.readline().rstrip().split("\t")

            if type(first_line) == list and (len(first_line) == 10 or len(first_line)==7):
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
<<<<<<< HEAD
=======

>>>>>>> fd9988560bbd6a0c888dc87011c6b7fc72041855
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

            def signed_check_MPU(num):
                if num > 32767:
                    num -= 65536
                return num
            def signed_check_AKM(num):
                if num > 32760:
                    num -= 65520
                return num

            three_num = []

            if MLSB =="MSB":
                a = lst[0]*256 + lst[1]*1
                b = lst[2]*256 + lst[3]*1
                c = lst[4]*256 + lst[5]*1

                three_num.append(signed_check_MPU(a))
                three_num.append(signed_check_MPU(b))
                three_num.append(signed_check_MPU(c))

            elif MLSB =="LSB":
                a = lst[1]*256 + lst[0]*1
                b = lst[3]*256 + lst[2]*1
                c = lst[5]*256 + lst[4]*1
                three_num.append(signed_check_AKM(a))
                three_num.append(signed_check_AKM(b))
                three_num.append(signed_check_AKM(c))

            return three_num

        s = self.fileLineEdit.text()
        s1 = s[:-4]

        f = open(u"%s" %s ,"r")
        w = open(u"%s_RESULT.txt" %s1, "w")
        w.close()

        data_line_list = []

        # save stripped data in list
        tick = 0
        one_line_result = ""


        for line in open(u"%s" %s ,"r"):
            data_line= f.readline()
            data_line_strip = data_line.strip()
            #data_line_list.append(data_line_strip)

            if tick == 0:
                result_list = data_line_strip
                one_line_result += result_list + "\t"
                tick += 1
            elif tick == 1:
                result_list = dec_2_hexdec(eval(data_line_strip))
                one_line_result += list_sep(result_list)
                tick += 1
            elif tick == 2:
                result_list = dec_2_hexdec(eval(data_line_strip))
                one_line_result += list_sep(result_list)
                tick += 1
            elif tick == 3:
                result_list = dec_2_hexdec(eval(data_line_strip), "LSB")
                one_line_result += list_sep(result_list)
                one_line_result

                w = open(u"%s_RESULT.txt" %s1, "a+")
                print >> w, one_line_result
                w.close()

                one_line_result=""
                tick = 0
                count +=1

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
        time_data_list = []

        if self.INHERIT_KEY == False:
            s = self.fileLineEdit.text()
            f = open(u"%s" %s ,"r")
            s1 = s[:-4]

            w = open(u"%s_TIME.txt" %s1, "w")
            w.close()

            data_line_strip = []

            for line in open(u"%s" %s ,"r"):
                data_line= f.readline()
                data_line_strip = data_line.strip().split("\t")
                time_data = data_line_strip[0]

                w = open(u"%s_TIME.txt" %s1, "a+")
                print >> w, time_data
                w.close()

        elif self.INHERIT_KEY == True:
            s = self.fileLineEdit.text()
            s1 = s[:-4]

            f = open(u"%s_RESULT.txt" %s1 ,"r")
            w = open(u"%s_RESULT_TIME.txt" %s1, "w")
            w.close()

            for line in open(u"%s_RESULT.txt" %s1 ,"r"):
                data_line= f.readline()
                data_line_strip = data_line.strip().split("\t")
                time_data = data_line_strip[0]

                w = open(u"%s_RESULT_TIME.txt" %s1, "a+")
                print >> w, time_data
                w.close()

        else:
            print "ERROR OCCUR!"


        f.close()
        w.close()

        t1=time.time()-t0
        self.statusBrowser.append(u"時間資訊分離完成，共花費%.2f秒" %t1)
        self.toPlot_button.setEnabled(True)


    def parseTimeDiff(self):
        t0 = time.time()
        self.statusBrowser.append(u"解算資料時間差...")

        if self.INHERIT_KEY == False:
            s = self.fileLineEdit.text()
            s1 = s[:-4]
            w = open(u"%s_TIMEDIFF.txt" %s1, "w")
            w.close()
            before_value = 0.0
            with open(u"%s" %s ,"r") as f:
                for line in f:
                        cc = float(line.strip().split("\t")[0]) - before_value
                        before_value = float(line.strip().split("\t")[0])
                        w = open(u"%s_TIMEDIFF.txt" %s1, "a+")
                        print >> w, cc
                        w.close()


        elif self.INHERIT_KEY == True:
            s = self.fileLineEdit.text()
            s1 = s[:-4]

            w = open(u"%s_RESULT_TIMEDIFF.txt" %s1, "w")
            w.close()
            before_value = 0.0
            with open(u"%s_RESULT.txt" %s1 ,"r") as f:
                for line in f:
                    cc = float(line.strip().split("\t")[0]) - before_value
                    before_value = float(line.strip().split("\t")[0])
                    w = open(u"%s_RESULT_TIMEDIFF.txt" %s1, "a+")
                    print >> w, cc
                    w.close()

        t1 = time.time()-t0

        self.statusBrowser.append(u"時間差資料分離完成，共花費%.2f秒" %t1)
        self.toPlot_button.setEnabled(True)


    def toPlot(self):
        if self.INHERIT_KEY == False:
            s = self.fileLineEdit.text()
            fname=u"%s" %s
            f = open(u"%s" %s ,"r")

        elif self.INHERIT_KEY ==True:
            s = self.fileLineEdit.text()
            s1 = s[:-4]
            fname = u"%s_RESULT.txt" %s1
            f = open(u"%s_RESULT.txt" %s1 ,"r")

        datatype=[('time',np.float32), ('ax',np.int16), ('ay',np.int16), ('az',np.int16),
                                            ('gx',np.int16), ('gy',np.int16), ('gz',np.int16),
                                            ('mx',np.int16), ('my',np.int16), ('mz',np.int16),
                                            ('time_diff', np.float32)]

        data = np.genfromtxt(fname, dtype=datatype, delimiter="\t")

        time_diff_array = np.diff(data['time'])
        time_diff_array = np.append(time_diff_array, [time_diff_array[-1]])

        data['time_diff'] = time_diff_array

        data_index = [ 'time', 'time_diff',
                        'ax', 'ay', 'az',
                        'gx', 'gy', 'gz',
                        'mx', 'my', 'mz']

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

        for i in range(len(checkbox_list)):
            if checkbox_list[i].isChecked():
                plt.plot(np.arange(0,data[data_index[i]].size),data[data_index[i]], label=data_index[i])
                self.statusBrowser.append(str(np.average(data[data_index[i]])))
                #print "check checked"

        plt.legend(loc='upper left')
        plt.title('result')

        plt.show()

if __name__ == "__main__":
	app=QApplication(sys.argv)
	Decode_GUI = Decode_GUI()
	Decode_GUI.show()
	sys.exit(app.exec_())
