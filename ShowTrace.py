#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author : MikeChan
# Email  : m7807031@gmail.com

import time, sys, os, threading
import pandas as pd
import numpy as np
from scipy import signal, optimize, stats, integrate
from sklearn.metrics import r2_score

import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

from PyQt4.QtCore import *
from PyQt4.QtGui import *



class IMU_trace(QWidget):
    # self.raw_data is all raw data!
    def __init__(self, parent = None):
        super(IMU_trace, self).__init__(parent)
        #self.setGeometry(200,50,350,150)
        self.move(10,10)

        self.setWindowTitle(u"產出軌跡程式")

        # create Layout and connection
        self.createLayout()
        self.createConnection()

        #bias dict
        self.bias_dict ={   'ax': 0.639909, 'ay': 142.6601, 'az': -824.501,
                            'gx': 35.61079, 'gy': 53.51407, 'gz': -135.055,
                            'mx':0 ,'my':0 ,'mz':0 }

        # set global varibles
        self.raw_data = np.array(0)

    def createLayout(self):
        self.fileLineEdit=QLineEdit()
        self.openfile_Button=QPushButton(u"選擇檔案")
        h0 = QHBoxLayout()
        h0.addWidget(self.fileLineEdit)
        h0.addWidget(self.openfile_Button)

        self.record_sec_le = QLineEdit()
        self.sec_label = QLabel(u'秒')
        self.set_record_sec_btn = QPushButton(u"輸入靜置秒數(預設=10s)")
        ht =QHBoxLayout()
        ht.addWidget(self.record_sec_le)
        ht.addWidget(self.sec_label)
        ht.addWidget(self.set_record_sec_btn)
        self.record_sec_le.setText(str(10))


        self.axis_choose_label = QLabel(u"軸向選取：ax")
        self.axis_choose_label.setAlignment(Qt.AlignCenter)
        self.axis_combobox = QComboBox()
        self.axis_combobox.addItems(['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'mx', 'my', 'mz'])
        h6=QHBoxLayout()
        h6.addWidget(self.axis_choose_label)
        h6.addWidget(self.axis_combobox)



        self.magic_label = QLabel(u"@===== 魔法按鈕 =====@")
        self.magic_label.setAlignment(Qt.AlignCenter)
        h00 = QHBoxLayout()
        h00.addWidget(self.magic_label)


        self.magic_2_button = QPushButton('magic! 2')
        self.magic_3_button = QPushButton('magic! 3')
        h000 = QHBoxLayout()

        h000.addWidget(self.magic_2_button)
        h000.addWidget(self.magic_3_button)


        self.trendLine_label = QLabel(u"@===== 1D資訊 =====@")
        self.trendLine_label.setAlignment(Qt.AlignCenter)
        h1 = QHBoxLayout()
        h1.addWidget(self.trendLine_label)

        self.show_raw_mean_le = QLineEdit()
        self.show_raw_mean_button = QPushButton(u'原始資料各軸平均')
        h1_0=QHBoxLayout()
        h1_0.addWidget(self.show_raw_mean_le)
        h1_0.addWidget(self.show_raw_mean_button)

        self.trendLine_content1_label = QLabel("Trendline: Y = AX + B")
        self.trendLine_content2_label = QLabel("R: NaN")
        self.trendLine_button = QPushButton(u"計算趨勢線")
        self.show_detrend_button = QPushButton(u"產出Detrend圖表")
        h1_1 = QHBoxLayout()
        h1_1.addWidget(self.trendLine_content1_label)
        h1_1.addWidget(self.trendLine_content2_label)
        h1_1.addWidget(self.trendLine_button)
        h1_1.addWidget(self.show_detrend_button)

        self.acc_label = QLabel(u"@===== 原始2D資訊 =====@")
        self.acc_label.setAlignment(Qt.AlignCenter)
        h2 = QHBoxLayout()
        h2.addWidget(self.acc_label)

        self.show_raw_2d_acc_Button = QPushButton(u"三軸加速度與積分")
        self.show_raw_2d_gyro_Button = QPushButton(u"三軸角速度與積分")
        self.show_raw_2d_mag_Button = QPushButton(u'三軸磁力值')
        h2_1 = QHBoxLayout()
        h2_1.addWidget(self.show_raw_2d_acc_Button)
        h2_1.addWidget(self.show_raw_2d_gyro_Button)
        h2_1.addWidget(self.show_raw_2d_mag_Button)


        self.gyro_label = QLabel(u"@===== 原始資料3D資訊 =====@")
        self.gyro_label.setAlignment(Qt.AlignCenter)
        h3 = QHBoxLayout()
        h3.addWidget(self.gyro_label)

        self.show_raw_3d_acctrace_Button = QPushButton(u"加速度軌跡")
        self.show_raw_3d_gyrotrace_Button = QPushButton(u"角速度軌跡")
        h3_1 = QHBoxLayout()
        h3_1.addWidget(self.show_raw_3d_acctrace_Button)
        h3_1.addWidget(self.show_raw_3d_gyrotrace_Button)


        self.horizontal_line = QLabel("+"*30 + "+++++++++" + "+"*30)
        self.horizontal_line.setAlignment(Qt.AlignCenter)
        h5_up=QHBoxLayout()
        h5_up.addWidget(self.horizontal_line)
        self.horizontal_line = QLabel("="*30 + "  Analyst  " + "="*30)
        self.horizontal_line.setAlignment(Qt.AlignCenter)
        h5=QHBoxLayout()
        h5.addWidget(self.horizontal_line)
        self.horizontal_line = QLabel("+"*30 + "+++++++++" + "+"*30)
        self.horizontal_line.setAlignment(Qt.AlignCenter)
        h5_d=QHBoxLayout()
        h5_d.addWidget(self.horizontal_line)


        self.godmode_label = QLabel(u"@===== 頻譜分析 =====@")
        self.godmode_label.setAlignment(Qt.AlignCenter)
        h9 = QHBoxLayout()
        h9.addWidget(self.godmode_label)

        self.godmode_Button1 = QPushButton(u"頻譜分析")
        self.godmode_Button2 = QPushButton(u"頻譜分析2")
        h9_1 = QHBoxLayout()
        h9_1.addWidget(self.godmode_Button1)
        h9_1.addWidget(self.godmode_Button2)


        self.filter_label = QLabel(u"@===== 濾波分析 =====@")
        self.filter_label.setAlignment(Qt.AlignCenter)
        h10 = QHBoxLayout()
        h10.addWidget(self.filter_label)


        self.filtbutter_lp_slider_label = QLabel("Cutoff: NaNHz; Wn:Nan")
        self.filtbutter_lp_slider = QSlider(Qt.Horizontal)
        self.filtbutter_lp_slider.setMinimum(1)
        self.filtbutter_lp_slider.setMaximum(1420)
        self.filtbutter_lp_slider.setValue(200)
        self.filtbutter_lp_slider.setTickInterval(1)
        self.filtbutter_lp_slider.setSingleStep(1)
        h10_1 = QHBoxLayout()
        h10_1.addWidget(self.filtbutter_lp_slider)
        h10_1.addWidget(self.filtbutter_lp_slider_label)


        self.filtfilt_Button = QPushButton(u"Lowpass")
        self.butterHP_Button = QPushButton(u"Highpass")
        h10_2 = QHBoxLayout()
        h10_2.addWidget(self.filtfilt_Button)
        h10_2.addWidget(self.butterHP_Button)


        self.butterBP_Button = QPushButton('BandPass')
        h10_3 = QHBoxLayout()
        h10_3.addWidget(self.butterBP_Button)

        self.lp_filt_3D_trace_Button = QPushButton('Lowpass Trace')
        h10_4 = QHBoxLayout()
        h10_4.addWidget(self.lp_filt_3D_trace_Button)


        self.fusion_label = QLabel(u"@===== 磁力測試 =====@")
        self.fusion_label.setAlignment(Qt.AlignCenter)
        h11 = QHBoxLayout()
        h11.addWidget(self.fusion_label)


        self.threshold_test_label = QLabel("Data not decide yet")
        self.threshold_test_button = QPushButton(u"門檻過濾測試用")
        h11_XX = QHBoxLayout()
        h11_XX.addWidget(self.threshold_test_label)
        h11_XX.addWidget(self.threshold_test_button)


        self.mag_scatter_label = QLabel("Data not decide yet")
        self.mag_scatter_button = QPushButton(u"原始磁力平面散佈圖")
        h11_00 = QHBoxLayout()
        h11_00.addWidget(self.mag_scatter_label)
        h11_00.addWidget(self.mag_scatter_button)


        self.mag_scatter_adj_label = QLabel("Data not decide yet")
        self.mag_scatter_adj_button = QPushButton(u"修正後磁力平面散佈圖")
        h11_000 = QHBoxLayout()
        h11_000.addWidget(self.mag_scatter_adj_label)
        h11_000.addWidget(self.mag_scatter_adj_button)



        self.mag_heading_label = QLabel("Mean Heading")
        self.raw_mag_heading_button = QPushButton(u"計算原始磁力角(無修正)")
        self.mag_heading_button = QPushButton(u"計算磁力角(無傾斜修正)")
        h11_0 = QHBoxLayout()
        h11_0.addWidget(self.mag_heading_label)
        h11_0.addWidget(self.raw_mag_heading_button)
        h11_0.addWidget(self.mag_heading_button)


        self.fusion_label = QLabel(u"@===== 9軸Fusion =====@")
        self.fusion_label.setAlignment(Qt.AlignCenter)
        h12 = QHBoxLayout()
        h12.addWidget(self.fusion_label)

        self.gravity_calibration_label = QLabel("roll:NaN; pitch:NaN")
        self.gravity_calibration_button = QPushButton(u"計算整體的RPH")
        h12_1 = QHBoxLayout()
        h12_1.addWidget(self.gravity_calibration_label)
        h12_1.addWidget(self.gravity_calibration_button)

        self.gravity_compensate_label =QLabel(u"消除重力影響")
        self.gravity_compensate_button = QPushButton(u'消除重力軌跡')
        h12_2=QHBoxLayout()
        h12_2.addWidget(self.gravity_compensate_label)
        h12_2.addWidget(self.gravity_compensate_button)

        self.acc_with_gyro_fusion_label =QLabel(u"以角速度修正 Body to NEH acc")
        self.acc_with_gyro_fusion_button = QPushButton(u"6軸Fusion產出軌跡")
        h12_3=QHBoxLayout()
        h12_3.addWidget(self.acc_with_gyro_fusion_label)
        h12_3.addWidget(self.acc_with_gyro_fusion_button)

        self.answer_trace_button = QPushButton(u'產出軌跡')
        h12_4 = QHBoxLayout()
        h12_4.addWidget(self.answer_trace_button)


        self.for_hofong_label = QLabel(u"@===== 后豐用? =====@")
        h13_0=QHBoxLayout()
        h13_0.addWidget(self.for_hofong_label)



        self.acc_integral_per_sec_label =QLabel(u"每秒加速度")
        self.generate_dist_per_sec_button = QPushButton(u"產出每秒移動距離")
        h13_1a = QHBoxLayout()
        h13_1a.addWidget(self.acc_integral_per_sec_label)
        h13_1a.addWidget(self.generate_dist_per_sec_button)


        self.gyro_integral_per_sec_label =QLabel(u"每秒旋轉角度")
        self.generate_degree_per_sec_button = QPushButton(u"產出內差一秒旋轉角度")
        h13_1b = QHBoxLayout()
        h13_1b.addWidget(self.gyro_integral_per_sec_label)
        h13_1b.addWidget(self.generate_degree_per_sec_button)


        self.interp_different_hz_label =QLabel(u"內差不同頻率旋轉角度")
        self.interp_different_hz_button = QPushButton(u"產出內差不同頻率旋轉角度")
        h13_2 = QHBoxLayout()
        h13_2.addWidget(self.interp_different_hz_label)
        h13_2.addWidget(self.interp_different_hz_button)

        self.trace_by_238mmpersec_with_degrees_label =QLabel(u"以秒速23.83cm產出軌跡")
        self.trace_by_238mmpersec_with_degrees_button = QPushButton(u"以秒速23.83cm+指定旋轉量產出軌跡")
        h13_3 = QHBoxLayout()
        h13_3.addWidget(self.trace_by_238mmpersec_with_degrees_label)
        h13_3.addWidget(self.trace_by_238mmpersec_with_degrees_button)


        layout = QVBoxLayout()
        layout.addLayout(h0)
        layout.addLayout(ht)
        layout.addLayout(h6)
        layout.addLayout(h00)
        layout.addLayout(h000)


        layout.addLayout(h1)
        layout.addLayout(h1_0)
        layout.addLayout(h1_1)
        layout.addLayout(h2)
        layout.addLayout(h2_1)
        layout.addLayout(h3)
        layout.addLayout(h3_1)
        layout.addLayout(h5_up)
        layout.addLayout(h5)
        layout.addLayout(h5_d)

        layout.addLayout(h9)
        layout.addLayout(h9_1)
        layout.addLayout(h10)
        layout.addLayout(h10_1)
        layout.addLayout(h10_2)
        layout.addLayout(h10_3)
        layout.addLayout(h10_4)
        layout.addLayout(h11)
        layout.addLayout(h11_XX)
        layout.addLayout(h11_00)
        layout.addLayout(h11_000)
        layout.addLayout(h11_0)
        layout.addLayout(h12)
        layout.addLayout(h12_1)
        layout.addLayout(h12_2)
        layout.addLayout(h12_3)
        layout.addLayout(h12_4)
        layout.addLayout(h13_0)
        layout.addLayout(h13_1a)
        layout.addLayout(h13_1b)
        layout.addLayout(h13_2)
        layout.addLayout(h13_3)

        '''
        # plot area!! =====================
        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas = FigureCanvas(self.figure)
        #self.canvas.setMinimumSize(1200,800)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.plot_button = QPushButton('Plot')

        plot_area = QVBoxLayout()
        plot_area.addWidget(self.toolbar)
        plot_area.addWidget(self.canvas)
        plot_area.addWidget(self.plot_button)
        '''
        layout_all = QGridLayout()
        layout_all.addLayout(layout,0,0)
        #layout_all.addLayout(plot_area,0,1)

        self.setLayout(layout_all)

    def createConnection(self):
        self.openfile_Button.clicked.connect(self.file_open)
        self.trendLine_button.clicked.connect(self.trendLine)
        self.show_detrend_button.clicked.connect(self.show_detrend)

        self.set_record_sec_btn.clicked.connect(self.set_record_sec)

        self.show_raw_mean_button.clicked.connect(self.show_raw_mean)
        self.magic_2_button.clicked.connect(self.magic2)
        self.magic_3_button.clicked.connect(self.magic3)

        self.show_raw_2d_acc_Button.clicked.connect(self.show_raw_2d_acc_data)
        self.show_raw_2d_gyro_Button.clicked.connect(self.show_raw_2d_gyro_data)
        self.show_raw_2d_mag_Button.clicked.connect(self.show_raw_2d_mag_data)
        self.show_raw_3d_acctrace_Button.clicked.connect(self.show_raw_3d_acctrace)
        self.show_raw_3d_gyrotrace_Button.clicked.connect(self.show_raw_3d_gyrotrace)

        self.axis_combobox.currentIndexChanged.connect(self.axis_choose)

        self.godmode_Button1.clicked.connect(self.fft_test)
        self.godmode_Button2.clicked.connect(self.fft_test2)

        self.filtbutter_lp_slider.valueChanged.connect(self.change_filtfilt_Wn)
        self.filtfilt_Button.clicked.connect(self.butterLP)
        self.butterHP_Button.clicked.connect(self.butterHP)
        self.butterBP_Button.clicked.connect(self.butterBP)
        self.lp_filt_3D_trace_Button.clicked.connect(self.lp_filt_3D_trace)

        self.threshold_test_button.clicked.connect(self.threshold_test)
        self.mag_scatter_button.clicked.connect(self.mag_scatter)
        self.mag_scatter_adj_button.clicked.connect(self.mag_scatter_adj)
        self.raw_mag_heading_button.clicked.connect(self.raw_mag_heading)
        self.mag_heading_button.clicked.connect(self.mag_heading_without_cali_tile)
        self.gravity_calibration_button.clicked.connect(self.gravity_calibration)
        self.gravity_compensate_button.clicked.connect(self.show_gravity_compensate)
        self.acc_with_gyro_fusion_button.clicked.connect(self.acc_with_gyro_fusion_output_new_acc)

        self.answer_trace_button.clicked.connect(self.answer_trace)

        self.generate_dist_per_sec_button.clicked.connect(self.generate_dist_per_sec)
        self.generate_degree_per_sec_button.clicked.connect(self.generate_degree_per_sec)
        self.interp_different_hz_button.clicked.connect(self.interp_different_hz)
        self.trace_by_238mmpersec_with_degrees_button.clicked.connect(self.trace_by_238mmpersec_with_degrees)

    '''#===== File reading section =====#'''
    def check_file_available(self, file):
        first_line = self.raw_file.readline()
        check_line = first_line.rstrip().split("\t")

        if len(check_line) == 10:  return True
        else:  return False

    def read_file_to_np(self, file_name):
        datatype =  [('time',np.float32), ('ax',np.int16), ('ay',np.int16), ('az',np.int16),
                            ('gx',np.int16), ('gy',np.int16), ('gz',np.int16),
                            ('mx',np.int16), ('my',np.int16), ('mz',np.int16),
                            ('time_diff', np.float32)]

        data = np.genfromtxt(file_name, dtype=datatype, delimiter="\t")

        data['time'] = data['time']-data['time'][0]

        a = np.diff(data['time'])
        time_diff_array = np.insert(a, 0, 0)
        data['time_diff'] = time_diff_array


        # 磁力值校正
        data['mx'] = data['mx'] * 1.18359375
        data['my'] = data['my'] * 1.19140625
        data['mz'] = data['mz'] * 1.14453125

        return data

    def show_error_message(self, index):
        if index == 0:
            error_file_popup = QMessageBox.warning(self, u'檔案錯誤!', u"請重新選擇檔案", QMessageBox.Cancel)
            self.fileLineEdit.setText("")
        elif index == 1:
            error_file_popup = QMessageBox.warning(self, u'定軸錯誤!', u"請重新輸入定軸", QMessageBox.Cancel)
        elif index == 2:
            error_file_popup = QMessageBox.information(self, u'讀取完成', u"檔案讀取完成!", QMessageBox.Ok)

    def file_open(self):
        fn = QFileDialog.getOpenFileName(self, 'Open File')
        self.fileLineEdit.setText(fn)
        self.raw_file = open(u'%s' %fn, 'r')

        if self.check_file_available(self.raw_file):
            self.raw_data = self.read_file_to_np(self.raw_file)
            self.show_error_message(2)
            self.show_raw_2d_acc_Button.setEnabled(True)
            self.show_raw_2d_gyro_Button.setEnabled(True)
            self.show_raw_3d_acctrace_Button.setEnabled(True)
            self.show_raw_3d_gyrotrace_Button.setEnabled(True)

        else:
            self.show_error_message(0)


    '''#===== Qitem Support =====#'''
    def axis_choose(self):
        self.axis_choose_label.setText(u"軸向選取： " + self.axis_combobox.currentText())

    def change_filtfilt_Wn(self):
        self.filtbutter_lp_slider_label.setText("Cutoff: " + str(self.filtbutter_lp_slider.value()/10.0)+ "Hz" +
                                                "; Wn: %.3f " %(self.filtbutter_lp_slider.value()/1430.0)  )

    def set_record_sec(self):
      num,ok = QInputDialog.getInt(self,u"IMU靜置時間",u"輸入此筆資料靜置秒數")
      if ok:
        self.record_sec_le.setText(str(num))

    '''#===== magic button =====#'''
    def magic2(self):
        ax = self.acc_normalize(self.raw_data['ax'])
        ay = self.acc_normalize(self.raw_data['ay'])
        az = self.acc_normalize(self.raw_data['az'])

        gx, dx, nx =  self.another_integral(self.gyro_normalize(self.raw_data['gx']))
        gy, dy, ny =  self.another_integral(self.gyro_normalize(self.raw_data['gy']))
        gz, dz, nz =  self.another_integral(self.gyro_normalize(self.raw_data['gz']))

        f,ax = plt.subplots(2, sharex=True)
        ax[0].set_title("gyro data drift")
        ax[0].plot(self.raw_data['gx'], label='gx')
        ax[0].plot(self.raw_data['gy'], label='gy')
        ax[0].plot(self.raw_data['gz'], label='gz')

        ax[1].plot(dx, label='dx')
        ax[1].plot(dy, label='dy')
        ax[1].plot(dz, label='dz')
        plt.show()

    def magic3(self):
        time_end = 5123

        real_hofong_fix_pts = pd.read_csv('20161012_HoFong/control_points_coodination.csv').sort(ascending=False)
        real_hofong_fix_pts['N'] = real_hofong_fix_pts['N'] - real_hofong_fix_pts['N'][129]
        real_hofong_fix_pts['E'] = real_hofong_fix_pts['E'] - real_hofong_fix_pts['E'][129] # last data name=2717, index=129


        N_diff = np.diff(real_hofong_fix_pts['N'])
        E_diff = np.diff(real_hofong_fix_pts['E'])

        hofong_deg = np.rad2deg(np.arctan2(N_diff, E_diff))
        hofong_deg = hofong_deg - hofong_deg[0]
        hofong_deg_diff = np.cumsum(np.diff(hofong_deg))

        interp_hofong = np.interp(np.arange(100), np.arange(hofong_deg_diff.size), hofong_deg_diff)


        #plt.plot(hofong_deg, label='hahaxd')
        #plt.plot(hofong_deg_diff, label='hehexd')
        plt.plot(interp_hofong)
        plt.legend()
        plt.show()

    '''#===== data normalizer =====#'''
    def acc_normalize(self, lst):
        #change gyro data from lSB to g then m/s^2
        #offset will be remove !

        stable_sec= int(self.record_sec_le.text())
        stable_count = int(stable_sec * (1/0.007))
        offset = np.average(lst[1:stable_count])
        #offset = 0

        np_acc_lst = np.array(lst)
        np_acc_normalized_list = (np_acc_lst - offset)* 9.80665 / 16384.0
        return np_acc_normalized_list

    def gyro_normalize(self, lst):
        #change gyro data from lSB to deg/s
        #offset will be remove !
        stable_sec= int(self.record_sec_le.text())
        stable_count = int(stable_sec * (1/0.007))
        offset = np.average(lst[1:stable_count])

        np_gyro_lst = np.array(lst)
        np_gyro_normalized_list = (np_gyro_lst - offset)/131.0
        #print np_gyro_normalized_list[5:15]
        return np_gyro_normalized_list

    def mag_adj(self):
        #打開磁力校正用檔案
        mag_cali_file = self.read_file_to_np("CALIBRATION_DATA/hofong_mag_cali_RESULT.txt")
        raw_data_size = self.raw_data['mx'].size
        #mx = self.raw_data['mx'].astype(np.float32) * 1.15625
        #my = self.raw_data['my'].astype(np.float32) * 1.1640625
        #mz = self.raw_data['mz'].astype(np.float32) * 1.11328125

        mx = np.append(self.raw_data['mx'].astype(np.float32), mag_cali_file['mx'].astype(np.float32))
        my = np.append(self.raw_data['my'].astype(np.float32), mag_cali_file['my'].astype(np.float32))
        mz = np.append(self.raw_data['mz'].astype(np.float32), mag_cali_file['mz'].astype(np.float32))

        m_normal = np.sqrt(np.square(mx)+np.square(my)+np.square(mz))
        mx_bias = (np.amax(mx) + np.amin(mx)) /2.
        my_bias = (np.amax(my) + np.amin(my)) /2.
        mz_bias = (np.amax(mz) + np.amin(mz)) /2.

        mx_scale = (np.amax(mx) - np.amin(mx)) /2.
        my_scale = (np.amax(my) - np.amin(my)) /2.
        mz_scale = (np.amax(mz) - np.amin(mz)) /2.
        avg_radius = (mx_scale + my_scale + mz_scale)/3.
        #avg_radius = 255

        #print avg_radius

        mx_rad_enlarge_times = avg_radius/mx_scale
        my_rad_enlarge_times = avg_radius/my_scale
        mz_rad_enlarge_times = avg_radius/mz_scale

        mx_adj = (mx-mx_bias)*mx_rad_enlarge_times
        my_adj = (my-my_bias)*my_rad_enlarge_times
        mz_adj = (mz-mz_bias)*mz_rad_enlarge_times

        mx_adj = mx_adj[:raw_data_size]
        my_adj = my_adj[:raw_data_size]
        mz_adj = mz_adj[:raw_data_size]

        return mx_adj, my_adj, mz_adj


    '''#===== 1D information =====#'''
    def trendLine(self, axis_choose=None):
        stable_sec= int(self.record_sec_le.text())
        stable_count = int(stable_sec * (1/0.007))

        if axis_choose:
            axis = axis_choose
        else:
            axis = str(self.axis_combobox.currentText())

        x = self.raw_data['time'][:stable_count]
        y = self.raw_data[axis][:stable_count]
        coefficients = np.polyfit(x,y,1)
        p = np.poly1d(coefficients)
        coefficient_of_dermination = r2_score(y, p(x))

        self.trendLine_content1_label.setText("Trendline: " + str(p))
        self.trendLine_content2_label.setText("R: " + str(coefficient_of_dermination))
        return coefficients

    def detrend(self, signal, coefficients):
        detrend_signal = []
        for i in range(signal.size):
            detrend_signal.append(signal[i] - (
                    (self.raw_data['time'][i]-self.raw_data['time'][0]) * coefficients[0] + coefficients[1]) )
        return detrend_signal

    def detrend_1d(self, signal, time_lst):
        stable_sec= int(self.record_sec_le.text())
        stable_count = int(stable_sec * (1/0.007))
        x = self.raw_data['time'][:stable_count]
        y = signal[:stable_count]
        coefficients = np.polyfit(x,y,1)

        detrend_signal = []
        for i in range(signal.size):
            detrend_signal.append(
                signal[i] - ((time_lst[i]-time_lst[0]) * coefficients[0] + coefficients[1])
                )
        return detrend_signal


    def show_detrend(self):
        if self.fileLineEdit.text().isEmpty(): self.show_error_message(index=0)

        gx_notrend,dx_notrend, nx_notrend = self.another_integral(self.gyro_normalize(self.detrend(self.raw_data['gx'], self.trendLine('gx'))))
        gy_notrend,dy_notrend, ny_notrend = self.another_integral(self.gyro_normalize(self.detrend(self.raw_data['gy'], self.trendLine('gy'))))
        gz_notrend,dz_notrend, nz_notrend = self.another_integral(self.gyro_normalize(self.detrend(self.raw_data['gz'], self.trendLine('gz'))))

        gx_g_array,gx_r_array, gx_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gx']))
        gy_g_array,gy_r_array, gy_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gy']))
        gz_g_array,gz_r_array, gz_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gz']))


        #===== gx =====
        plt.subplot(231)
        plt.plot(gx_g_array, "blue", label="gx")
        plt.plot(gx_notrend, "r", label = "gx_notrend", alpha=0.7)
        plt.legend(loc='best')

        plt.subplot(234)
        plt.plot(gx_r_array, "blue", label="dx")
        plt.plot(dx_notrend, "r", label = "dx_notrend", alpha=0.7)
        plt.legend(loc='best')

        #===== gy =====
        plt.subplot(232)
        plt.plot(gy_g_array, "blue", label="gy")
        plt.plot(gy_notrend, "r", label = "gy_notrend", alpha=0.7)
        plt.legend(loc='best')

        plt.subplot(235)
        plt.plot(gy_r_array, "blue", label="dy")
        plt.plot(dy_notrend, "r", label = "dy_notrend", alpha=0.7)
        plt.legend(loc='best')

        #===== gz =====
        plt.subplot(233)
        plt.plot(gz_g_array, "blue", label="gz")
        plt.plot(gz_notrend, "r", label = "gz_notrend", alpha=0.7)
        plt.legend(loc='best')

        plt.subplot(236)
        plt.plot(gz_r_array, "blue", label="dz")
        plt.plot(dz_notrend, "r", label = "dz_notrend", alpha=0.7)
        plt.legend(loc='best')

        #===== show plot =====
        plt.show()

    '''#===== Show Raw Data's integral ====='''
    def show_raw_mean(self):
        if self.fileLineEdit.text().isEmpty(): self.show_error_message(index=0)
        ax_mean = np.mean(self.raw_data['ax'])
        ay_mean = np.mean(self.raw_data['ay'])
        az_mean = np.mean(self.raw_data['az'])
        gx_mean = np.mean(self.raw_data['gx'])
        gy_mean = np.mean(self.raw_data['gy'])
        gz_mean = np.mean(self.raw_data['gz'])
        mx_mean = np.mean(self.raw_data['mx'])
        my_mean = np.mean(self.raw_data['my'])
        mz_mean = np.mean(self.raw_data['mz'])

        show_text = u"mean_a_g_m:\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f" \
         %(ax_mean, ay_mean, az_mean, gx_mean, gy_mean, gz_mean, mx_mean, my_mean, mz_mean)

        self.show_raw_mean_le.setText(show_text)

    def show_raw_2d_acc_data(self):
        if self.fileLineEdit.text().isEmpty(): self.show_error_message(index=0)
        ax_a_array,ax_v_array,ax_s_array = self.another_integral(self.acc_normalize(self.raw_data['ax']))
        ay_a_array,ay_v_array,ay_s_array = self.another_integral(self.acc_normalize(self.raw_data['ay']))
        az_a_array,az_v_array,az_s_array = self.another_integral(self.acc_normalize(self.raw_data['az']))
        #plt.plot(np.insert(np.diff(ax_a_array),0,0) +500, "r", label="ax")
        #plt.plot(np.insert(np.diff(ay_a_array),0,0) +0, "g", label="ay")
        #plt.plot(np.insert(np.diff(az_a_array),0,0) -500, "b", label="az")

        '''
        s = ""
        w = open('acc_integrate_data.txt', 'w')
        print >> w, "ax\tay\taz"
        for i in range(ax_s_array.size):
            s = str(ax_s_array[i]) + "\t" + str(ay_s_array[i]) + "\t" +str(az_s_array[i])
            print >> w, s
            s=""
        w.close()
        '''

        #===== ax =====
        plt.subplot(331)
        plt.plot(ax_a_array, "blue", label="ax_a")
        plt.legend(loc='upper right')

        plt.subplot(334)
        plt.plot(ax_v_array, "blue", label="ax_v")
        plt.legend(loc='upper right')

        plt.subplot(337)
        plt.plot(ax_s_array, "blue", label="ax_s")
        plt.legend(loc='upper right')

        #===== ay =====
        plt.subplot(332)
        plt.plot(ay_a_array, "green", label="ay_a")
        plt.legend(loc='upper right')

        plt.subplot(335)
        plt.plot(ay_v_array, "green", label="ay_v")
        plt.legend(loc='upper right')

        plt.subplot(338)
        plt.plot(ay_s_array, "green", label="ay_s")
        plt.legend(loc='upper right')

        #===== az =====
        plt.subplot(333)
        plt.plot(az_a_array, "red", label="az_a")
        plt.legend(loc='upper right')

        plt.subplot(336)
        plt.plot(az_v_array, "red", label="az_v")
        plt.legend(loc='upper right')

        plt.subplot(339)
        plt.plot(az_s_array, "red", label="az_s")
        plt.legend(loc='upper right')


        plt.show()

    def show_raw_3d_acctrace(self):
        if len(self.raw_data) < 1:
            self.show_error_message(0)
        else:
            ax_array,vx_array,sx_array = self.another_integral(self.acc_normalize(self.raw_data['ax']))
            ay_array,vy_array,sy_array = self.another_integral(self.acc_normalize(self.raw_data['ay']))
            az_array,vz_array,sz_array = self.another_integral(self.acc_normalize(self.raw_data['az']))

            mpl.rcParams['legend.fontsize'] = 24
            fig = plt.figure()
            ax = fig.gca(projection='3d')
            ax.set_aspect('equal')

            x = sx_array
            y = sy_array
            z = sz_array

            ax.set_xlabel('X axis')
            ax.set_ylabel('Y axis')
            ax.set_zlabel('Z axis')

            max_axis_value = max(np.amax(x), np.amax(y), np.amax(z))
            min_axis_value = min(np.amin(x), np.amin(y), np.amin(z))

            ax.set_xlim(min_axis_value,max_axis_value)
            ax.set_ylim(min_axis_value,max_axis_value)
            ax.set_zlim(min_axis_value,max_axis_value)

            ax.plot(x, y, z, 'b-',  linewidth=2.0, label='tracker')
            ax.plot(x, y, zs=min_axis_value, c='k' , zdir='z') # shadow on XY plane
            ax.plot(y, z, min_axis_value, c='k' , zdir='x') #

            #ax.annotate("start point", xyz=(x[0],y[0],z[0]), xyztext=(x[0]+1, y[0]+1, z[0]+1), arrowprops=dict(facecolor='black', shrink=0.05) )

            '''
            ax.annotate( "Value",
            xy = (x[0], y[0]), xytext = (x[0]-20, y[0]-20), textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
            '''


            ax.legend()

            plt.show()

    def show_raw_2d_gyro_data(self):
        if self.fileLineEdit.text().isEmpty(): self.show_error_message(index=0)
        gx_g_array,gx_r_array, gx_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gx']))
        gy_g_array,gy_r_array, gy_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gy']))
        gz_g_array,gz_r_array, gz_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gz']))


        #===== gx =====
        plt.subplot(231)
        plt.plot(gx_g_array, "blue", label="gx_g")
        plt.legend(loc='best')

        plt.subplot(234)
        plt.plot(gx_r_array, "blue", label="gx_r")
        plt.legend(loc='best')

        #===== gy =====
        plt.subplot(232)
        plt.plot(gy_g_array, "green", label="gy_g")
        plt.legend(loc='best')

        plt.subplot(235)
        plt.plot(gy_r_array, "green", label="gy_r")
        plt.legend(loc='best')

        #===== gz =====
        plt.subplot(233)
        #plt.plot(gz_array,"b", label="no diff bias")
        plt.plot(gz_g_array, "red", label="gz_g")
        plt.legend(loc='best')

        plt.subplot(236)
        #plt.plot(np.rad2deg(dz_array),"b", label="no diff bias")
        plt.plot(gz_r_array, "red", label="gz_r")

        plt.legend(loc='best')

        plt.show()

    def show_raw_3d_gyrotrace(self):

        if len(self.raw_data) < 1:
            self.show_error_message(0)
        else:
            gx_g_array,gx_r_array, gx_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gx']))
            gy_g_array,gy_r_array, gy_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gy']))
            gz_g_array,gz_r_array, gz_no_array = self.another_integral(self.gyro_normalize(self.raw_data['gz']))

            mpl.rcParams['legend.fontsize'] = 18
            fig = plt.figure()
            ax = fig.gca(projection='3d')
            ax.set_aspect('equal')

            x = gx_r_array
            y = gy_r_array
            z = gz_r_array

            ax.set_xlabel('rx axis')
            ax.set_ylabel('ry axis')
            ax.set_zlabel('rz axis')

            ax.set_xlim(np.amin(x),np.amax(x))
            ax.set_ylim(np.amin(y),np.amax(y))
            ax.set_zlim(np.amin(z),np.amax(z))
            ax.plot(x, y, z, 'r-', label='tracker')

            ax.legend()
            plt.grid()
            plt.show()

    def show_raw_2d_mag_data(self):
        mx = self.raw_data['mx']
        my = self.raw_data['my']
        mz = self.raw_data['mz']

        mx_adj, my_adj, mz_adj = self.mag_adj()

        plt.subplot(211)
        plt.plot(mx, 'blue', label='mx')
        plt.plot(my, 'green', label='my')
        plt.plot(mz, 'red', label='mz')

        plt.subplot(212)
        plt.plot(mx_adj, 'blue', label='mx_adj')
        plt.plot(my_adj, 'green', label='my_adj')
        plt.plot(mz_adj, 'red', label='mz_adj')

        plt.legend(loc='upper right', fontsize=16)
        plt.show()


    '''#===== algorithm =====#'''
    def moving_average(self, a, n=101) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def another_integral(self,lst, time_lst=None):
        acc = np.array(lst, dtype=np.float32)
        if time_lst != None:
            time = time_lst
        else:
            time = self.raw_data['time']
        vel = integrate.cumtrapz(acc, time, initial=0)
        dist = integrate.cumtrapz(vel, time, initial=0)
        return acc, vel, dist

    def basic_basic_integral(self, target_list, time_diff_list=None):
        a_array = target_list

        if time_diff_list:
            time_diff_array = time_diff_list
        else:
            time_diff_array = self.raw_data['time_diff'].copy()
        #time_diff_array= np.ones(self.raw_data['time'].size)
        v_array = [0]
        s_array = [0]

        for i in range(time_diff_array.size):
            s_data = s_array[-1] + v_array[-1] * time_diff_array[i] + 0.5 * a_array[i] * (time_diff_array[i]**2 )
            s_array.append(s_data)

            v_data= v_array[-1] + a_array[i] * time_diff_array[i]
            v_array.append(v_data)

        v_array = np.array(v_array, np.float32)
        s_array = np.array(s_array, np.float32)


        return a_array, v_array, s_array

    #r=roll, p=pitch, h= heading
    def rotate_array(self, roll, pitch, heading):
        r= roll
        p= pitch
        h= heading

        C_a2b = np.array([
            [np.cos(p)*np.cos(h),    np.cos(p)*np.sin(h),   -1*np.sin(p)],
            [np.sin(r)*np.sin(p)*np.cos(h)-np.cos(r)*np.sin(h),    np.sin(r)*np.sin(p)*np.sin(h)+np.cos(r)*np.cos(h), np.sin(r)*np.cos(p)],
            [np.cos(r)*np.sin(p)*np.cos(h)+np.sin(r)*np.sin(h),    np.cos(r)*np.sin(p)*np.sin(h)-np.sin(r)*np.cos(h), np.cos(r)*np.cos(p)]
        ])
        return C_a2b

    def threshold_test(self):
        mx_adj, my_adj, mz_adj = self.mag_adj()
        m_normal = np.sqrt(np.square(mx_adj)+np.square(my_adj)+np.square(mz_adj))

        heading = np.degrees(np.arctan2(mx_adj/m_normal, my_adj/m_normal))

        heading_diff = np.diff(heading)

        rotate_index =  np.insert(np.where(np.absolute(heading_diff)>20.0), 0, 0)

        plt.plot(heading_diff)
        plt.show()

        angle_lst = []
        for i in range(rotate_index.size):
            try:
                angle_onestep = np.mean(heading[rotate_index[i]: rotate_index[i+1]])
                angle_lst.append(angle_onestep)
            except:
                pass

        print angle_lst

    def std_threshold(self, lst):      #將指定門檻職以外的砍除
        lst = np.array(lst)
        index_array = []
        threshold = 10
        a = np.insert(np.where(np.diff(lst)>threshold),0,0)
        a = np.append(a, lst.size)
        lst_2 = lst.copy()
        for i in range(a.size-1):
            lst_2[a[i]:a[i+1]+1] = np.mean(lst[a[i]:a[i+1]+1])

        return lst_2


    '''#===== Filter Area =====#'''
    def fft_test(self):
        #t = np.arange(0, 1.0, 1.0/8000)
        #signal = np.sin(2*np.pi*156.25*t)  + 2*np.sin(2*np.pi*234.375*t)
        axis = str(self.axis_combobox.currentText())
        signal = self.raw_data[axis] - self.bias_dict[axis]

        n = signal.size
        time_step = 0.007
        fftResult = (np.abs(np.fft.fft(signal)/n))**2
        freq = np.fft.fftfreq(n, d=time_step)

        plt.plot(1/freq, fftResult, 'g')
        plt.xlim(0)
        plt.grid('on')
        plt.title('Power Spectrum')
        plt.show()

    def fft_test2(self):
        axis = str(self.axis_combobox.currentText())

        if axis.startswith('a'):
            normal_para = 16384.0
        elif axis.startswith('g'):
            normal_para = 131.0
        signal =( self.raw_data[axis] - self.bias_dict[axis])/ normal_para

        n = signal.size # Number of data points
        dx = 0.007 # Sampling period (in meters)
        Fk = np.fft.fft(signal) # Fourier coefficients (divided by n)
        nu = np.fft.fftfreq(n,dx) # Natural frequencies
        #Fk = np.fft.fftshift(Fk) # Shift zero freq to center
        #nu = np.fft.fftshift(nu) # Shift zero freq to center
        f, ax = plt.subplots(3,1,sharex=True)
        ax[0].plot(nu, np.real(Fk)) # Plot Cosine terms
        ax[0].set_ylabel(r'$Re[F_k]$', size = 'x-large')
        ax[1].plot(nu, np.imag(Fk)) # Plot Sine terms
        ax[1].set_ylabel(r'$Im[F_k]$', size = 'x-large')
        ax[2].plot(nu, np.absolute(Fk)**2) # Plot spectral power
        ax[2].set_ylabel(r'$\vert F_k \vert ^2$', size = 'x-large')
        ax[2].set_xlabel(r'$\widetilde{\nu}$', size = 'x-large')
        plt.title(axis)
        plt.show()

    def butterLP(self):
        #===== parameter =====
        coefficients = self.trendLine()
        axis = str(self.axis_combobox.currentText())
        N=10
        time_interval = 0.007
        sample_rate = int(1/time_interval)
        Nquist_freq = 0.5 * sample_rate
        Wn = float(self.filtbutter_lp_slider.value()) / 1430.0

        #===== input =====
        if axis[0] =='a':
            input_signal = self.acc_normalize(self.raw_data[axis])
        elif axis[0]=='g':
            input_signal = self.gyro_normalize(self.raw_data[axis])
        elif axis[0]=='m':
            input_signal = self.raw_data[axis]

        #===== caculation area =====
        b, a = signal.butter(N, Wn, 'low')
        #d, c = signal.bessel(N, Wn, 'low')

        butter_lp_signal = signal.filtfilt(b, a, input_signal)


        #===== output =====
        raw_a, raw_v, raw_s = self.another_integral(input_signal)
        butter_lp_a, butter_lp_v, butter_lp_s = self.another_integral(butter_lp_signal)  #butter_lp_signal
        #bessel_lp_a, bessel_lp_v, bessel_lp_s = self.basic_basic_integral(bessel_lp_signal)
        print "Max: " + str(max(butter_lp_s)) + "; Min: " + str(min(butter_lp_s))

        #===== raw vs filt =====
        plt.title(axis)
        plt.subplot(311)
        plt.grid(True)
        plt.plot(raw_a, "blue", label="raw_a")
        plt.plot(butter_lp_a, "red", label="butter_lp_a")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(312)
        plt.grid(True)
        plt.plot(raw_v, "blue", label="raw_a")
        plt.plot(butter_lp_v, "red", label="butter_lp_v")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(313)
        plt.grid(True)
        plt.plot(raw_s, "blue", label="raw_a")
        plt.plot(butter_lp_s, "red", label="butter_lp_s")
        plt.legend(loc=2, fontsize = 'medium')


        plt.show()

        self.filtbutter_lp_slider.setFocus()

    def butterHP(self):
        #===== parameter =====
        axis = str(self.axis_combobox.currentText())
        N=10
        time_interval = 0.007
        sample_rate = int(1/time_interval)
        Nquist_freq = 0.5 * sample_rate
        Wn = float(self.filtbutter_lp_slider.value()) / 1430.0
        #===== input =====
        if axis[0] =='a':
            input_signal = self.acc_normalize(self.raw_data[axis])
        elif axis[0]=='g':
            input_signal = self.gyro_normalize(self.raw_data[axis])

        #===== caculation area =====
        b, a = signal.butter(N, Wn, 'high')
        output_signal = signal.filtfilt(b, a, input_signal)

        #===== output =====
        raw_a, raw_v, raw_s = self.basic_basic_integral(input_signal)
        butter_hp_a, butter_hp_v, butter_hp_s = self.basic_basic_integral(output_signal)

        #===== raw vs filt =====
        plt.subplot(311)
        plt.grid(True)
        plt.plot(raw_a, "blue", label="raw_a")
        plt.plot(butter_hp_a, "red", label="butter_hp_a")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(312)
        plt.grid(True)
        plt.plot(raw_v, "blue", label="raw_a")
        plt.plot(butter_hp_v, "red", label="butter_hp_v")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(313)
        plt.grid(True)
        plt.plot(raw_s, "blue", label="raw_a")
        plt.plot(butter_hp_s, "red", label="butter_hp_s")
        plt.legend(loc=2, fontsize = 'medium')

        '''
        #===== raw integral
        plt.subplot(323)
        plt.plot(raw_v, "blue", label="raw_v")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(325)
        plt.plot(raw_s, "blue", label="raw_s")
        plt.legend(loc=2, fontsize = 'medium')

        #===== filter integral
        plt.subplot(324)
        plt.plot(butter_hp_v, "red", label="butter_hp_v")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(326)
        plt.plot(butter_hp_s, "red", label="butter_hp_s")
        plt.legend(loc=2, fontsize = 'medium')
        '''

        plt.legend(loc=2,prop={'size':12})
        plt.title(axis)
        plt.show()
        self.filtbutter_lp_slider.setFocus()

    def butterBP(self):
        axis = str(self.axis_combobox.currentText())
        N=10
        time_interval = 0.007
        sample_rate = int(1/time_interval)
        Nquist_freq = 0.5 * sample_rate

        Wn_low = float(self.filtbutter_lp_slider.value()) / 1430.0
        Wn_band_range = 0.5
        Wn = [  Wn_low,  Wn_low+Wn_band_range ]
        #===== input =====
        if axis[0] =='a':
            input_signal = self.acc_normalize(self.raw_data[axis])
        elif axis[0]=='g':
            input_signal = self.gyro_normalize(self.raw_data[axis])

        #===== caculation area =====
        b, a = signal.butter(N, Wn, 'bandstop')
        output_signal = signal.filtfilt(b, a, input_signal)

        #===== output =====
        raw_a, raw_v, raw_s = self.basic_basic_integral(input_signal)
        butter_bp_a, butter_bp_v, butter_bp_s = self.basic_basic_integral(output_signal)


        #===== raw vs filt =====
        plt.subplot(311)
        plt.plot(raw_a, "blue", label="raw_a")
        plt.plot(butter_bp_a, "red", label="butter_bp_a")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(312)
        plt.plot(raw_v, "blue", label="raw_a")
        plt.plot(butter_bp_v, "red", label="butter_bp_v")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(313)
        plt.plot(raw_s, "blue", label="raw_a")
        plt.plot(butter_bp_s, "red", label="butter_bp_s")
        plt.legend(loc=2, fontsize = 'medium')

        '''
        #===== raw integral
        plt.subplot(323)
        plt.plot(raw_v, "blue", label="raw_v")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(325)
        plt.plot(raw_s, "blue", label="raw_s")
        plt.legend(loc=2, fontsize = 'medium')

        #===== filter integral
        plt.subplot(324)
        plt.plot(butter_bp_v, "red", label="butter_bp_v")
        plt.legend(loc=2, fontsize = 'medium')

        plt.subplot(326)
        plt.plot(butter_bp_s, "red", label="butter_bp_s")
        plt.legend(loc=2, fontsize = 'medium')
        '''

        plt.legend(loc=2,prop={'size':12})
        plt.title(axis)
        plt.show()
        self.filtbutter_lp_slider.setFocus()

    def lp_filt_3D_trace(self):
        #===== parameter =====
        #coefficients_ax = self.trendLine('ax')
        #coefficients_ay = self.trendLine('ay')
        #coefficients_az = self.trendLine('az')

        N=10
        time_interval = 0.007
        sample_rate = int(1/time_interval)
        Nquist_freq = 0.5 * sample_rate
        Wn = float(self.filtbutter_lp_slider.value()) / 1430.0


        #ax_ng, ay_ng, az_ng = self.gravity_compensate()
        #input_signal_ax = self.acc_normalize(ax_ng)
        #input_signal_ay = self.acc_normalize(ay_ng)
        #input_signal_az = self.acc_normalize(az_ng)

        input_signal_ax = self.acc_normalize(self.raw_data['ax'])
        input_signal_ay = self.acc_normalize(self.raw_data['ay'])
        input_signal_az = self.acc_normalize(self.raw_data['az'])

        #===== caculation area =====
        b, a = signal.butter(N, Wn, 'low')

        butter_lp_signal_ax = signal.filtfilt(b, a, input_signal_ax)
        butter_lp_signal_ay = signal.filtfilt(b, a, input_signal_ay)
        butter_lp_signal_az = signal.filtfilt(b, a, input_signal_az)


        def detrend(signal, coefficients):
            detrend_signal = []
            for i in range(signal.size):
                detrend_signal.append(signal[i] - (
                        (self.raw_data['time'][i]-self.raw_data['time'][0]) * coefficients[0] + coefficients[1]) )
            return detrend_signal

        #===== output =====
        lp_ax_a, lp_ax_v, lp_ax_s = self.basic_basic_integral(butter_lp_signal_ax)  #butter_lp_signal
        lp_ay_a, lp_ay_v, lp_ay_s = self.basic_basic_integral(butter_lp_signal_ay)
        lp_az_a, lp_az_v, lp_az_s = self.basic_basic_integral(butter_lp_signal_az)
        #lp_ax_a, lp_ax_v, lp_ax_s = self.basic_basic_integral(detrend(butter_lp_signal_ax, coefficients_ax))  #butter_lp_signal
        #lp_ay_a, lp_ay_v, lp_ay_s = self.basic_basic_integral(detrend(butter_lp_signal_ay, coefficients_ay))
        #lp_az_a, lp_az_v, lp_az_s = self.basic_basic_integral(detrend(butter_lp_signal_az, coefficients_az))

        #===== plot =====
        mpl.rcParams['legend.fontsize'] = 24
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        x = np.array(lp_ax_s)
        y = np.array(lp_ay_s)
        z = np.array(lp_az_s)


        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_zlabel('Z axis')

        max_axis_value = max(np.amax(x), np.amax(y), np.amax(z))
        min_axis_value = min(np.amin(x), np.amin(y), np.amin(z))

        ax.set_xlim(min_axis_value,max_axis_value)
        ax.set_ylim(min_axis_value,max_axis_value)
        ax.set_zlim(min_axis_value,max_axis_value)

        ax.plot(x, y, z, 'r-',  linewidth=2.0, label='tracker')
        ax.plot(x, y, zs=min_axis_value, c='k' , zdir='z') # shadow on XY plane
        ax.plot(y, z, min_axis_value, c='k' , zdir='x') #

        ax.plot([0],[0],[0],'bo', linewidth=5.0)

        ax.legend()
        plt.grid()

        plt.show()


    '''#===== Show Mag ====='''
    def mag_scatter(self):
        mx = self.raw_data['mx'].astype(np.float32)
        my = self.raw_data['my'].astype(np.float32)
        mz = self.raw_data['mz'].astype(np.float32)
        #m_normal = np.sqrt(np.square(mx)+np.square(my)+np.square(mz))
        plt.xlim(-1000., 1000.)
        plt.ylim(-1000., 1000.)

        plt.plot(mx, my, "ro", label='mxy')
        plt.plot(mx, mz, "go", label='mxz')
        plt.plot(my, mz, "yo", label='myz')
        plt.legend(loc='upper left')
        plt.show()

    def mag_scatter_adj(self):
        mx_adj, my_adj, mz_adj = self.mag_adj()
        print "offset: mx=%.6f; my=%.6f; mz=%.6f" %(np.mean(mx_adj), np.mean(my_adj), np.mean(mz_adj))

        self.mag_scatter_adj_label.setText(u"offset: mx=%.2f; my=%.2f; mz=%.2f" %(np.mean(mx_adj), np.mean(my_adj), np.mean(mz_adj)))

        plt.xlim(-1000., 1000.)
        plt.ylim(-1000., 1000.)
        plt.plot(mx_adj, my_adj, "ro", label='mxy')
        plt.plot(mx_adj, mz_adj, "go", label='mxz')
        plt.plot(my_adj, mz_adj, "yo", label='myz')
        plt.legend(loc='upper left')
        plt.show()

    def raw_mag_heading(self):
        mx = self.raw_data['mx'].astype(np.float32)
        my = self.raw_data['my'].astype(np.float32)
        mz = self.raw_data['mz'].astype(np.float32)
        m_normal = np.sqrt(np.square(mx)+np.square(my)+np.square(mz))


        heading = np.arctan2(mx/m_normal, my/m_normal)
        roll = np.arctan2(my/m_normal, mz/m_normal)
        pitch = np.arctan2(mx/m_normal, mz/m_normal)


        plt.plot(np.degrees(heading), "red", label="heading")
        #plt.plot(np.degrees(roll), "green", label="roll")
        #plt.plot(np.degrees(pitch), "blue", label="pitch")
        #plt.plot(m_normal, "yellow", label='m_normal')
        plt.legend(loc='upper left')
        plt.show()

    def mag_heading_without_cali_tile(self):
        mx_adj, my_adj, mz_adj = self.mag_adj()
        m_normal = np.sqrt(np.square(mx_adj)+np.square(my_adj)+np.square(mz_adj))

        plt.plot(mx_adj, "g", label="mx_adj")
        plt.plot(my_adj, "b", label="my_adj")
        #plt.plot(mz_adj, "r", label="mz_adj")
        plt.show()

        '''
        def moving_average(a, n=3) :
            ret = np.cumsum(a, dtype=float)
            ret[n:] = ret[n:] - ret[:-n]
            return ret[n - 1:] / n

        mx_adj_movinga = moving_average(mx_adj, 10000)
        my_adj_movinga = moving_average(my_adj, 10000)
        mz_adj_movinga = moving_average(mz_adj, 10000)
        m_normal = np.sqrt(np.square(mx_adj_movinga)+np.square(my_adj_movinga)+np.square(mz_adj_movinga))
        m_normal = 1
        '''

        heading = np.arctan2(mx_adj/m_normal, my_adj/m_normal)
        roll = np.arctan2(my_adj/m_normal, mz_adj/m_normal)
        pitch = np.arctan2(mx_adj/m_normal, mz_adj/m_normal)


        plt.plot(np.degrees(heading), "red", label="heading")
        #plt.plot(np.degrees(roll), "green", label="roll")
        #plt.plot(np.degrees(pitch), "blue", label="pitch")
        #plt.plot(m_normal, "yellow", label='m_normal')
        plt.legend(loc='upper left')
        plt.show()


    '''#===== Show Gravity effect =====#'''
    def gravity_calibration(self):
        time_diff = self.raw_data['time_diff']
        ax = self.raw_data['ax'].astype(np.float32) -self.bias_dict['ax']
        ay = self.raw_data['ay'].astype(np.float32) -self.bias_dict['ay']
        az = self.raw_data['az'].astype(np.float32)- self.bias_dict['az']
        a_normal = np.sqrt(np.square(ax)+np.square(ay)+np.square(az))

        raw_gx = self.raw_data['gx'].astype(np.float32) -self.bias_dict['gx']
        raw_gy = self.raw_data['gy'].astype(np.float32) -self.bias_dict['gy']
        raw_gz = self.raw_data['gz'].astype(np.float32) -self.bias_dict['gz']

        gx, dx, nx = self.another_integral(self.gyro_normalize(raw_gx))
        gy, dy, ny = self.another_integral(self.gyro_normalize(raw_gy))
        gz, dz, nz = self.another_integral(self.gyro_normalize(raw_gz))

        mx, my, mz = self.mag_adj()
        m_normal = np.sqrt(np.square(mx)+np.square(my)+np.square(mz))

        #計算由重力值取得之 roll and pitch
        #_pitch = 1* np.arctan2(ay , np.sqrt(np.square(ay)+np.square(az)))
        #_roll = 1* np.arctan2(az, np.sqrt(np.square(ax)+np.square(az)))
        _roll = 1* np.arctan2(ay, az) #重力於YZ平面上分量 與z軸夾角
        _pitch = 1* np.arctan2(ax , az) # 重力於XZ平面上分量與Z軸夾角


        #計算經由傾角校正後之磁力值 Heading
        mn_x = mx * np.cos(_roll) + my * np.sin(_roll) * np.sin(_pitch) - mz*np.cos(_pitch)*np.sin(_roll)
        mn_y = my * np.cos(_pitch) + mz * np.sin(_pitch)
        mn_normal = np.sqrt(np.square(mn_x)+np.square(mn_y)+np.square(mz))
        _heading = np.arctan2(mn_x, mn_y)
        #heading = np.arctan2(mx/m_normal, my/m_normal)


        #===== Plot area =====
        #===== RPH from gravity vs gyro_integrate =====
        plt.subplot(311)
        plt.grid(True)
        plt.plot(dx, "blue", label="dx")
        plt.plot(np.degrees(_roll), "red", label="roll")
        plt.legend(loc='best', fontsize = 'medium')

        plt.subplot(312)
        plt.grid(True)
        plt.plot(dy, "blue", label="dy")
        plt.plot(np.degrees(_pitch), "red", label="pitch")
        plt.legend(loc='best', fontsize = 'medium')

        plt.subplot(313)
        plt.grid(True)
        plt.plot(dz, "blue", label="dz")
        plt.plot(np.degrees(_heading), "red", label="heading")
        plt.legend(loc='best', fontsize = 'medium')

        print u"起點磁力角: %.2f"  %( np.average(np.degrees(_heading)[:10000]))
        print u"終點磁力角: %.2f"  %( np.average(np.degrees(_heading)[-10000:]))
        plt.show()

    def gravity_compensate(self, input_sec=120): #利用前置秒數重力值RPH修正全段傾斜狀況
        input_cutoff_sec = input_sec
        raw_time = self.raw_data['time']

        # 找出指定秒數對應的筆數
        over_cutoff_time_array = raw_time[np.where(raw_time>input_cutoff_sec)]
        stable_state_end_counts=  np.where(raw_time == over_cutoff_time_array[0])[0]

        #計算前置秒數內三軸加速度的平均值
        ax = self.raw_data['ax'].astype(np.float32)[0:stable_state_end_counts]- self.bias_dict['ax']
        ay = self.raw_data['ay'].astype(np.float32)[0:stable_state_end_counts]- self.bias_dict['ay']
        az = self.raw_data['az'].astype(np.float32)[0:stable_state_end_counts]- self.bias_dict['az']
        a_normal = np.sqrt(np.square(ax) + np.square(ay) + np.square(az))

        raw_ax = self.raw_data['ax'].astype(np.float32)- self.bias_dict['ax']
        raw_ay = self.raw_data['ay'].astype(np.float32)- self.bias_dict['ay']
        raw_az = self.raw_data['az'].astype(np.float32)- self.bias_dict['az']



        '''
        #=============== 舊的平均ROLL 與 PITCH 與 旋轉矩陣 =============
        #在指定前置秒數的穩定狀態下，僅依靠重力獲得的 平均Roll 跟 平均Pitch
        mean_roll = -np.mean(np.arctan2(
                        ay/a_normal ,
                        np.sqrt(np.square(ay/a_normal) +  np.square(az/a_normal))
                        ))

        mean_pitch = -np.mean(np.arctan2(-ay/a_normal , az/a_normal))


        #C_n2b 為 NEU to BFS system 旋轉矩陣
        C_n2b = np.array(
            [
                [                  np.cos(mean_roll),                0,                      -1*np.sin(mean_roll) ],
                [    np.sin(mean_roll)*np.sin(mean_pitch),    np.cos(mean_pitch),     np.sin(mean_pitch)*np.cos(mean_roll) ],
                [    np.cos(mean_pitch)*np.sin(mean_roll),    -1*np.sin(mean_pitch),        np.cos(mean_pitch)*np.cos(mean_roll) ]
            ])
        #=============== 舊的平均ROLL 與 PITCH 與 旋轉矩陣  END=============
        '''

        #=============== 新的平均ROLL 與 PITCH 與 旋轉矩陣 =============
        #在指定前置秒數的穩定狀態下，僅依靠重力獲得的 平均Roll 跟 平均Pitch
        mean_roll = np.mean(np.arctan2(ay/a_normal , az/a_normal))
        mean_pitch = np.mean(np.arctan2(ax/a_normal , az/a_normal))

        #C_n2b 為 NEU to BFS system 旋轉矩陣
        C_n2b = np.array(
            [
                [                  np.cos(mean_pitch),                0,                      -1*np.sin(mean_pitch) ],
                [    np.sin(mean_roll)*np.sin(mean_pitch),    np.cos(mean_roll),     np.sin(mean_roll)*np.cos(mean_pitch) ],
                [    np.cos(mean_roll)*np.sin(mean_pitch),    -1*np.sin(mean_roll),        np.cos(mean_roll)*np.cos(mean_pitch) ]
            ])
        #=============== 新的平均ROLL 與 PITCH 與 旋轉矩陣 END =============

        #C_b2n 為 BFS to NEU 的旋轉矩陣
        C_b2n = np.linalg.inv(C_n2b)

        #將[ax...],[ay...],[az...] 轉成 [(ax,ay,az), (ax,ay,az)....]
        adj_acc3_zip= zip(raw_ax, raw_ay, raw_az)

        acc3_normalize_T = []
        for i in range(len(adj_acc3_zip)):
            adj_acc3_zip_T = np.array(adj_acc3_zip[i])[:, np.newaxis]   #將zip後的資料先轉換成 3*1 形式
            acc3_normalize_T.append(np.dot(C_b2n,adj_acc3_zip_T))
        #print len(acc3_normalize_T)

        acc3_normalize=[]
        for i in range(len(acc3_normalize_T)):
            acc3_normalize.append(acc3_normalize_T[i].T)
        #print len(acc3_normalize)

        acc3_normalize_2 = []
        for i in acc3_normalize:
            acc3_normalize_2.append(i[0])

        adj_acc3_unzip = zip(*acc3_normalize_2)

        ax_caligravity = np.array(adj_acc3_unzip[0])
        ay_caligravity = np.array(adj_acc3_unzip[1])
        az_caligravity = np.array(adj_acc3_unzip[2])

        return ax_caligravity, ay_caligravity, az_caligravity

    def show_gravity_compensate(self):
        ax_nogravity, ay_nogravity, az_nogravity = self.gravity_compensate()

        ax_a_array,ax_v_array,ax_s_array = self.basic_basic_integral(self.acc_normalize(self.raw_data['ax']))
        ay_a_array,ay_v_array,ay_s_array = self.basic_basic_integral(self.acc_normalize(self.raw_data['ay']))
        az_a_array,az_v_array,az_s_array = self.basic_basic_integral(self.acc_normalize(self.raw_data['az']))

        ax_a_array_ng, ax_v_array_ng, ax_s_array_ng = self.basic_basic_integral(self.acc_normalize(ax_nogravity))
        ay_a_array_ng, ay_v_array_ng, ay_s_array_ng = self.basic_basic_integral(self.acc_normalize(ay_nogravity))
        az_a_array_ng, az_v_array_ng, az_s_array_ng = self.basic_basic_integral(self.acc_normalize(az_nogravity))

        #===== ax =====
        mpl.rcParams.update({'font.size': 14})
        plt.subplot(331)
        plt.plot(ax_a_array, "blue", label="ax_a")
        plt.plot(ax_a_array_ng, "red", label="ax_a_ng")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(334)
        plt.plot(ax_v_array, "blue", label="ax_v")
        plt.plot(ax_v_array_ng, "red", label="ax_v_ng")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(337)
        plt.plot(ax_s_array, "blue", label="ax_s")
        plt.plot(ax_s_array_ng, "red", label="ax_s_ng")
        plt.legend(loc='best', prop={'size':14})

        #===== ay =====
        plt.subplot(332)
        plt.plot(ay_a_array, "green", label="ay_a")
        plt.plot(ay_a_array_ng, "red", label="ay_a_ng")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(335)
        plt.plot(ay_v_array, "green", label="ay_v")
        plt.plot(ay_v_array_ng, "red", label="ay_v_ng")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(338)
        plt.plot(ay_s_array, "green", label="ay_s")
        plt.plot(ay_s_array_ng, "red", label="ay_s_ng")
        plt.legend(loc='best', prop={'size':14})

        #===== az =====
        plt.subplot(333)
        plt.plot(az_a_array, "purple", label="az_a")
        plt.plot(az_a_array_ng, "red", label="az_a_ng")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(336)
        plt.plot(az_v_array, "purple", label="az_v")
        plt.plot(az_v_array_ng, "red", label="az_v_ng")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(339)
        plt.plot(az_s_array, "purple", label="az_s")
        plt.plot(az_s_array_ng, "red", label="az_s_ng")
        plt.legend(loc='best', prop={'size':14})

        plt.show()

    def acc_with_gyro_fusion_output_new_acc(self):
        time = self.raw_data['time']
        time_diff = self.raw_data['time_diff']
        ax_degravity, ay_degravity, az_degravity = self.gravity_compensate()

        raw_ax = self.raw_data['ax'].astype(np.float32)-self.bias_dict['ax']
        raw_ay = self.raw_data['ay'].astype(np.float32)-self.bias_dict['ay']
        raw_az = self.raw_data['az'].astype(np.float32)-self.bias_dict['az']

        raw_gx = self.raw_data['gx'].astype(np.float32)-self.bias_dict['gx']
        raw_gy = self.raw_data['gy'].astype(np.float32)-self.bias_dict['gy']
        raw_gz = self.raw_data['gz'].astype(np.float32)-self.bias_dict['gz']

        gx, dx, nx = self.basic_basic_integral(self.gyro_normalize(raw_gx))
        gy, dy, ny = self.basic_basic_integral(self.gyro_normalize(raw_gy))
        gz, dz, nz = self.basic_basic_integral(self.gyro_normalize(raw_gz))

        _pitch = np.insert(np.arctan2(ax_degravity , np.sqrt(np.square(ay_degravity)+np.square(az_degravity))),0,0)
        _roll = np.insert(np.arctan2(-1*ay_degravity, az_degravity),0,0)

        w = self.filtbutter_lp_slider.value()/1430.0 #真實的給予角速度的權重
        print "degrees weight: " + str(w)
        weighted_roll = (1-w)*_roll + w * np.radians(dx)
        weighted_pitch = (1-w)*_pitch + w * np.radians(dy)

        adj_rotate_array = []
        for i in range(dx.size):
            #a = rotate_array(np.radians(dx_diff[i]), np.radians(dy_diff[i]), np.radians(dz_diff[i])) #獲得每個count時候的逆旋轉矩陣
            #a = rotate_array(np.radians(dx[i]), np.radians(dy[i]), np.radians(dz[i]))
            a = self.rotate_array(weighted_roll[i], weighted_pitch[i], np.radians(dz)[i])
            adj_rotate_array.append(a)

        #用旋轉矩陣修正 ax, ay, az
        axis3_zip_array = zip(ax_degravity, ay_degravity, az_degravity)
        new_axis3_T =[]
        for i in range(len(axis3_zip_array)):
            axis3_transpose = np.array(axis3_zip_array[i])[:, np.newaxis]
            new_axis3= np.dot( np.linalg.inv(adj_rotate_array[i]), axis3_transpose)
            new_axis3_T.append(new_axis3)

        kk = []
        for i in new_axis3_T:
            kk.append(i.T[0])

        new_new_axis3 = zip(*kk)

        new_new_ax = np.array(new_new_axis3[0])
        new_new_ay = np.array(new_new_axis3[1])
        new_new_az = np.array(new_new_axis3[2])


        new_ax, new_vx, new_sx = self.basic_basic_integral(self.acc_normalize(new_new_ax))
        new_ay, new_vy, new_sy = self.basic_basic_integral(self.acc_normalize(new_new_ay))
        new_az, new_vz, new_sz = self.basic_basic_integral(self.acc_normalize(new_new_az))

        ori_ax, ori_vx, ori_sx = self.basic_basic_integral(self.acc_normalize(raw_ax))
        ori_ay, ori_vy, ori_sy = self.basic_basic_integral(self.acc_normalize(raw_ay))
        ori_az, ori_vz, ori_sz = self.basic_basic_integral(self.acc_normalize(raw_az))

        print "====="
        print "Sx max: " + str(np.amax(new_sx)) + "; Sx min: " +  str(np.amin(new_sx))
        print "Sy max: " + str(np.amax(new_sy)) + "; Sy min: " +  str(np.amin(new_sy))
        print "Sz max: " + str(np.amax(new_sz)) + "; Sz min: " +  str(np.amin(new_sz))
        #===== plot area =====
        #===== ax =====
        plt.subplot(331)
        plt.plot(ori_ax, "blue", label="ori_ax")
        plt.plot(new_ax, "red", label="new_ax")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(334)
        plt.plot(ori_vx, "blue", label="ori_vx")
        plt.plot(new_vx, "red", label="new_vx")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(337)
        plt.plot(ori_sx, "blue", label="ori_sx")
        plt.plot(new_sx, "red", label="new_sx")
        plt.legend(loc='best', prop={'size':14})

        #===== ay =====
        plt.subplot(332)
        plt.plot(ori_ay, "green", label="ori_ay")
        plt.plot(new_ay, "red", label="new_ay")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(335)
        plt.plot(ori_vy, "green", label="ori_vy")
        plt.plot(new_vy, "red", label="new_vy")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(338)
        plt.plot(ori_sy, "green", label="ori_sy")
        plt.plot(new_sy, "red", label="new_sy")
        plt.legend(loc='best', prop={'size':14})

        #===== az =====
        plt.subplot(333)
        plt.plot(ori_az, "indigo", label="ori_az")
        plt.plot(new_az, "red", label="new_az")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(336)
        plt.plot(ori_vz, "indigo", label="ori_vz")
        plt.plot(new_vz, "red", label="new_vz")
        plt.legend(loc='best', prop={'size':14})

        plt.subplot(339)
        plt.plot(ori_sz, "indigo", label="ori_sz")
        plt.plot(new_sz, "red", label="new_sz")
        plt.legend(loc='best', prop={'size':14})

        plt.show()


    '''#===== Show Answer Trace =====#'''
    def answer_trace(self):
        error_file_popup = QMessageBox.warning(self, u'解算後軌跡!', u"軌跡成功解算喔!", QMessageBox.Ok)

    '''#===== For HoFong Trace =====#'''
    def generate_dist_per_sec(self):
        time_end= int(np.amax(self.raw_data['time']))

        #===== acc =====
        #先計算 x, y 方向分量數值的平方和根號，再做正規化後進行積分。
        ax_interp_10ms = self.acc_normalize(np.interp(np.arange(0.0,time_end,0.01), self.raw_data['time'], self.raw_data['ax']))
        ay_interp_10ms = self.acc_normalize(np.interp(np.arange(0.0,time_end,0.01), self.raw_data['time'], self.raw_data['ay']))
        rxy_interp_10ms = np.sqrt(ax_interp_10ms**2 + ay_interp_10ms**2)

        plt.plot(ax_interp_10ms, c='b')
        plt.plot(ay_interp_10ms, c='g')
        plt.plot(self.detrend_1d(rxy_interp_10ms, time_lst=np.arange(0.0,time_end,0.01)), c='k')

        plt.show()

        axy, vxy, sxy = self.another_integral(rxy_interp_10ms, time_lst= np.arange(0.0,time_end,0.01))
        return axy, vxy, sxy

    def generate_degree_per_sec(self):
        time_end = int(np.amax(self.raw_data['time']))
        gx_interp_1s = np.interp(np.arange(time_end), self.raw_data['time'], self.raw_data['gx']) #內差成1S
        gy_interp_1s = np.interp(np.arange(time_end), self.raw_data['time'], self.raw_data['gy'])
        gz_interp_1s = np.interp(np.arange(time_end), self.raw_data['time'], self.raw_data['gz'])
        time = self.raw_data['time']

        gx, dx, nx = self.another_integral(self.gyro_normalize(self.raw_data['gx']))
        gy, dy, ny = self.another_integral(self.gyro_normalize(self.raw_data['gy']))
        gz, dz, nz = self.another_integral(self.gyro_normalize(self.raw_data['gz']))
        gx_1s, dx_1s, nx_1s = self.another_integral(self.gyro_normalize(gx_interp_1s), time_lst=np.arange(time_end))
        gy_1s, dy_1s, ny_1s = self.another_integral(self.gyro_normalize(gy_interp_1s), time_lst=np.arange(time_end))
        gz_1s, dz_1s, nz_1s = self.another_integral(self.gyro_normalize(gz_interp_1s), time_lst=np.arange(time_end))


        #gx, dx
        plt.subplot(231)
        plt.plot(time, gx, label='raw_gx')
        plt.plot(np.arange(time_end), gx_1s, c='r', label='interp_gx')
        plt.legend(loc='best')

        plt.subplot(234)
        plt.plot(time, dx, label='raw_dx')
        plt.plot(np.arange(time_end), dx_1s, c='r', label='interp_dx')
        plt.legend(loc='best')

        #gy, dy
        plt.subplot(232)
        plt.plot(time, gy, label='raw_gy')
        plt.plot(np.arange(time_end), gy_1s, c='r', label='interp_gy')
        plt.legend(loc='best')

        plt.subplot(235)
        plt.plot(time, dy, label='raw_dy')
        plt.plot(np.arange(time_end), dy_1s, c='r', label='interp_dy')
        plt.legend(loc='best')

        #gz, dz
        plt.subplot(233)
        plt.plot(time, gz, label='raw_gz')
        plt.plot(np.arange(time_end), gz_1s, c='r', label='interp_gz')
        plt.legend(loc='best')

        plt.subplot(236)
        plt.plot(time, dz, label='raw_dz')
        plt.plot(np.arange(time_end), dz_1s, c='r', label='interp_dz')
        plt.legend(loc='best')

        plt.show()

    def interp_different_hz(self):
        time = self.raw_data['time']
        time_end = int(np.amax(self.raw_data['time']))
        gz_interp_10ms = np.interp(np.arange(0.0,time_end,0.01), self.raw_data['time'], self.raw_data['gz'], left=0)
        gz_interp_1s = np.interp(np.arange(time_end), self.raw_data['time'], self.raw_data['gz'])

        gz, dz, nz = self.another_integral(self.gyro_normalize(self.raw_data['gz']))
        gz_10ms, dz_10ms, nz_10ms = self.another_integral(self.gyro_normalize(gz_interp_10ms), time_lst=np.arange(0.0,time_end,0.01))
        gz_1s, dz_1s, nz_1s = self.another_integral(self.gyro_normalize(gz_interp_1s), time_lst=np.arange(time_end))

        #===== Hofon tie point =====
        real_hofong_fix_pts = pd.read_csv('20161012_HoFong/control_points_coodination.csv').sort(ascending=False)
        real_hofong_fix_pts['N'] = real_hofong_fix_pts['N'] - real_hofong_fix_pts['N'][129]
        real_hofong_fix_pts['E'] = real_hofong_fix_pts['E'] - real_hofong_fix_pts['E'][129] # last data name=2717, index=129

        N_diff = np.diff(real_hofong_fix_pts['N'])
        E_diff = np.diff(real_hofong_fix_pts['E'])


        hofong_deg = np.rad2deg(np.arctan2(N_diff, E_diff))
        hofong_deg = hofong_deg - hofong_deg[0]
        hofong_deg_diff = np.cumsum(np.diff(hofong_deg))
        interp_hofong = np.interp(np.arange(time_end), np.arange(hofong_deg_diff.size), hofong_deg_diff)

        #===== plot area =====
        plt.subplot(211)
        plt.plot(time, gz, c='g', label='raw_gz')
        plt.plot(np.arange(0.0,time_end,0.01), gz_10ms, c='r', label='gz_10ms')
        plt.plot(np.arange(time_end), gz_1s, c='b', label='gz_1s')
        #plt.plot(np.arange(time_end), gz_hof, c='k', label='gz_hofong')
        plt.legend(loc='best')

        plt.subplot(212)
        plt.plot(time, dz, c='g', label='raw_dz')
        plt.plot(np.arange(0.0,time_end,0.01), dz_10ms, c='r', label='dz_10ms')
        plt.plot(np.arange(time_end), dz_1s, c='b', label='dz_1s')
        #plt.plot(np.arange(time_end), interp_hofong, c='k', linewidth=3, label='dz_hofong')
        plt.legend(loc='best')

        plt.grid()
        plt.show()


    def trace_by_238mmpersec_with_degrees(self):
        azi_angle = 28.95

        #===== acc catcher =====
        axy, vxy, sxy = self.generate_dist_per_sec()

        #===== gyro =====
        real_hofong_fix_pts = pd.read_csv('20161012_HoFong/control_points_coodination.csv')
        real_hofong_fix_pts['N'] = real_hofong_fix_pts['N'] - real_hofong_fix_pts['N'][129]
        real_hofong_fix_pts['E'] = real_hofong_fix_pts['E'] - real_hofong_fix_pts['E'][129] # last data name=2717, index=129

        time_end = int(np.amax(self.raw_data['time']))

        gz_interp_1ms = np.interp(np.arange(0.0,time_end,0.001), self.raw_data['time'], self.raw_data['gz'])
        gz_interp_10ms = np.interp(np.arange(0.0,time_end,0.01), self.raw_data['time'], self.raw_data['gz'])
        gz_interp_100ms = np.interp(np.arange(0.0,time_end,0.1), self.raw_data['time'], self.raw_data['gz'])
        gz_interp_1s = np.interp(np.arange(time_end), self.raw_data['time'], self.raw_data['gz'])

        gz_1ms, dz_1ms, nz_1ms = self.another_integral(self.gyro_normalize(gz_interp_1ms), time_lst=np.arange(0.0,time_end,0.001))
        gz_10ms, dz_10ms, nz_10ms = self.another_integral(self.gyro_normalize(gz_interp_10ms), time_lst=np.arange(0.0,time_end,0.01))
        gz_100ms, dz_100ms, nz_100ms = self.another_integral(self.gyro_normalize(gz_interp_100ms), time_lst=np.arange(0.0,time_end,0.1))
        gz_1s, dz_1s, nz_1s = self.another_integral(self.gyro_normalize(gz_interp_1s), time_lst=np.arange(0.0,time_end,1.0))
        gz, dz, nz = self.another_integral(self.gyro_normalize(self.raw_data['gz']))

        #假設每筆資料間隔0.007秒 固定速度0.17cm/s
        x_array = np.cumsum(  np.cos(np.deg2rad(dz-azi_angle)) * 0.17 /100.0)
        y_array = np.cumsum(np.sin(np.deg2rad(dz-azi_angle)) * 0.17 /100.0)

        x_10ms_array = np.cumsum(np.cos(np.deg2rad(dz_10ms-azi_angle)) * 0.2383 /100.0)
        y_10ms_array = np.cumsum(np.sin(np.deg2rad(dz_10ms-azi_angle)) * 0.2383 /100.0)

        new_x_10ms_array = np.cumsum(np.cos(np.deg2rad(dz_10ms-azi_angle))* np.insert(np.diff(sxy/10000),0,0))
        new_y_10ms_array = np.cumsum(np.sin(np.deg2rad(dz_10ms-azi_angle))* np.insert(np.diff(sxy/10000),0,0))

        x_1s_array = np.cumsum(np.cos(np.deg2rad(dz_1s-azi_angle)) * 23.83 /100.0)
        y_1s_array = np.cumsum(np.sin(np.deg2rad(dz_1s-azi_angle)) * 23.83 /100.0)


        plt.plot(x_array, y_array, label = u'without interp, assuming every move is 0.17cm/s')
        plt.plot(x_10ms_array, y_10ms_array, c='g', label=u'interp angle to 10ms, assuming every sec speed is 0.2383cm/s')
        plt.plot(new_x_10ms_array, new_y_10ms_array, c='y', label=u'with real acc, angle has been interp to 10ms')
        plt.plot(x_1s_array, y_1s_array, c='r', label=u'interp angle to 1s, assuming every sec speed is 23.83cm/s')

        plt.plot(real_hofong_fix_pts['E'], real_hofong_fix_pts['N'], c='k', linewidth=3, label='HoFong real trace')
        plt.axes().set_aspect('equal')
        plt.grid()
        plt.legend(loc='best')
        plt.show()


if __name__ == "__main__":
	app=QApplication(sys.argv)
	show_trace = IMU_trace()
	show_trace.show()
	sys.exit(app.exec_())
