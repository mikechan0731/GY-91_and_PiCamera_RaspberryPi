#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author : MikeChan
# Email  : m7807031@gmail.com
# Date   : 06/21/2016

import time, sys, os, datetime, threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#===== Global Varibles =====
now = datetime.datetime.now()
today = str( str(now).split(" ")[0].split("-")[0] + str(now).split(" ")[0].split("-")[1] + str(now).split(" ")[0].split("-")[2] )
tonow = str( str(now).split(" ")[1].split(":")[0] + str(now).split(" ")[1].split(":")[1] )
countdown_sec = 0

#===== for raspberry PI =====
import smbus
import picamera
i2c = smbus.SMBus(1)
#enable pi-camera
try:
    camera = picamera.PiCamera()
except:
    pass
addr = 0x68
raw_data = []


#====== QT area ======
class IMU_GUI(QWidget):
    global countdown_sec
    def __init__(self, parent = None):
        super(IMU_GUI, self).__init__(parent)
        self.imu_start_record = imu_start_record()
        self.imu_start_record_stable = imu_start_record_stable()
        self.save_record = save_record()

        # create Layout and connection
        self.createLayout()
        self.createConnection()

        # window properties adjustment
        self.setGeometry(140,70,300,400)
        #self.resize(300,400)
        #self.move(140,35)
        self.setWindowIcon(QIcon('/home/pi/Self_IMU/icon/QIMU.png'))
        self.setWindowTitle("MPU9250 & PiCamera GUI")

        # varibles
        self.preview_switch = False
        self.film_switch = False
        self.IMU_KEY = False
        self.PAUSE_KEY = False
        self.photo_count = 0
        self.video_count = 0

        self.path = "%s_%s" % (today, tonow)
        if not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except OSError:
                if not os.path.isdir(self.path):
                    raise

    def createLayout(self):

        #===== IMU Layout =====
        self.IMU_Label = QLabel("@ IMU Area @")
        self.stableCheckBox = QCheckBox(u"即時慢速寫入")
        self.stableCheckBox.setChecked(True)
        h0=QHBoxLayout()
        h0.addWidget(self.IMU_Label)
        h0.addWidget(self.stableCheckBox)

        self.record_sec_le = QLineEdit()
        self.sec_label = QLabel(u'分')
        self.set_record_sec_btn = QPushButton(u"輸入幾分鐘(0=無限)")
        h01 =QHBoxLayout()
        h01.addWidget(self.record_sec_le)
        h01.addWidget(self.sec_label)
        h01.addWidget(self.set_record_sec_btn)
        self.record_sec_le.setText(str(0))

        self.statusBrowser  = QTextBrowser()
        h1 = QHBoxLayout()
        h1.addWidget(self.statusBrowser)

        self.startButton = QPushButton("Start IMU")
        self.pauseButton = QPushButton("Pause/Resume")
        self.stopButton = QPushButton("Stop IMU")
        self.saveButton = QPushButton("Save Data")
        h2 = QHBoxLayout()
        h2.addWidget(self.startButton)
        #h2.addWidget(self.pauseButton)
        h2.addWidget(self.stopButton)
        h2.addWidget(self.saveButton)


        #===== PiCamera layout ======
        self.PiCamera_Label = QLabel("@ PiCamera Area @")
        h3=QHBoxLayout()
        h3.addWidget(self.PiCamera_Label)

        self.camBrowser  = QTextBrowser()
        h4 = QHBoxLayout()
        h4.addWidget(self.camBrowser)

        self.previewButton = QPushButton("Preview")
        self.filmButton = QPushButton("Filming")
        self.photoButton = QPushButton("Photo Take")
        h5 = QHBoxLayout()
        h5.addWidget(self.previewButton)
        h5.addWidget(self.filmButton)
        h5.addWidget(self.photoButton)

        # setting layout
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout0 = QVBoxLayout()


        # IMU Layout
        layout1.addLayout(h0)
        layout1.addLayout(h01)
        layout1.addLayout(h1)
        layout1.addLayout(h2)

        # PiCamera Layout
        layout2.addLayout(h3)
        layout2.addLayout(h4)
        layout2.addLayout(h5)

        layout0.addLayout(layout1)
        layout0.addLayout(layout2)

        self.setLayout(layout0)

        self.previewButton.setEnabled(True)
        self.filmButton.setEnabled(True)
        self.photoButton.setEnabled(True)
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.saveButton.setEnabled(False)

    def createConnection(self):
        #===== IMU related =====
        self.set_record_sec_btn.clicked.connect(self.set_record_sec)
        self.startButton.clicked.connect(self.start)
        self.pauseButton.clicked.connect(self.pause)
        self.stopButton.clicked.connect(self.stop)
        self.saveButton.clicked.connect(self.save)
        #self.connect(self.save_record, SIGNAL("finished()"), self.finished)

        #===== Picamera related =====
        self.previewButton.clicked.connect(self.preview)
        self.filmButton.clicked.connect(self.film)
        self.photoButton.clicked.connect(self.take_photo)


        #====== Stable CheckBox related =====
        self.stableCheckBox.stateChanged.connect(self.enable_stable)

    #===== IMU Func. area =====
    def set_record_sec(self):
      num,ok = QInputDialog.getInt(self,u"預計IMU紀錄時間",u"輸入想要紀錄幾分鐘")
      if ok:
         self.record_sec_le.setText(str(num))

    def start(self):
        test_t0 = time.time()
        countdown_sec = self.record_sec_le.text() * 60
        self.statusBrowser.append("MPU9250 BootUp...")

        #===== IMU initial =====
        try:
            i2c.write_byte_data(0x68, 0x6a, 0x00)  # Clear sleep mode bit (6), enable all sensors
            time.sleep(0.1)  # Wait for all registers to reset

            i2c.write_byte_data(0x68, 0x1a, 0x03)
            # Configure Gyro and Thermometer
            # Disable FSYNC and set thermometer and gyro bandwidth to 41 and 42 Hz, respectively;
            # minimum delay time for this setting is 5.9 ms, which means sensor fusion update rates cannot
            # be higher than 1 / 0.0059 = 170 Hz
            # DLPF_CFG = bits 2:0 = 011; this limits the sample rate to 1000 Hz for both
            # With the MPU9250, it is possible to get gyro sample rates of 32 kHz (!), 8 kHz, or 1 kHz

            i2c.write_byte_data(0x68, 0x19, 0x04)
            # sample_rate = internal_sample_rate/ (1+SMPLRT_DIV)
            # Use a 200 Hz rate; a rate consistent with the filter update rate
            #determined inset in CONFIG above

            #ACC_CFG = i2c.read_byte_data(0x68, 0x1c)
            #ACC_CFG_2 = i2c.read_byte_data(0x68, 0x1D)
            #GYRO_CFG = i2c.read_byte_data(0x68, 0x1b)


            i2c.write_byte_data(0x68, 0x37, 0x02) # set pass-through mode
            time.sleep(0.1)

            i2c.write_byte_data(0x0c, 0x0a, 0x16) # enable AKM
            time.sleep(0.1)

            self.statusBrowser.append("Initialization Done!")
            self.IMU_KEY = True

        except:
            self.statusBrowser.append("Bootup Failed! Check Wiring...")
            self.IMU_KEY = False

            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.saveButton.setEnabled(False)
        #===== end initial ======

        countdown_sec = int(self.record_sec_le.text()) *60
        s = u"預定記錄秒數: %ss" %countdown_sec
        self.statusBrowser.append(s)


        #確認 stable checkbox 是否開啟
        if self.IMU_KEY and not self.stableCheckBox.isChecked():
            self.tt0 = time.time()
            self.statusBrowser.append(u"開始紀錄...")
            self.imu_start_record.start()

        elif self.IMU_KEY and self.stableCheckBox.isChecked():
            self.tt0 = time.time()
            self.statusBrowser.append(u"即時存檔狀態->開始紀錄...")
            self.imu_start_record_stable.start()



        # 防誤觸鎖鍵
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.saveButton.setEnabled(False)



    def pause(self):
        if not self.stableCheckBox.isChecked():
            if self.PAUSE_KEY == False:
                self.imu_start_record.stop()

            elif self.PAUSE_KEY == True:
                self.imu_start_record.start()

        elif self.stableCheckBox.isChecked():
            if self.PAUSE_KEY == False:
                self.imu_start_record_stable.stop()
            elif self.PAUSE_KEY == True:
                self.imu_start_record_stable.start()

        self.PAUSE_KEY = not self.PAUSE_KEY

    def stop(self):
        global raw_data

        self.duringTime = time.time() - self.tt0
        self.statusBrowser.append(u"停止紀錄!")
        self.statusBrowser.append("During Time: " + "%.2f" %self.duringTime)

        if not self.stableCheckBox.isChecked():
            self.imu_start_record.stop()
            self.save()
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.saveButton.setEnabled(True)
            self.statusBrowser.append(u"=檔案儲存完畢，清除 IMU 連線=")
            i2c.write_byte_data(addr, 0x6A, 0x07)

        elif self.stableCheckBox.isChecked():
            self.imu_start_record_stable.stop()
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.saveButton.setEnabled(False)
            self.statusBrowser.append(u"=檔案儲存完畢，清除 IMU 連線=")
            i2c.write_byte_data(addr, 0x6A, 0x07)


    def save(self):
        self.statusBrowser.append(u"檔案儲存中")
        time.sleep(0.5)
        self.save_record.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.saveButton.setEnabled(False)

    def finished(self):     # will be call when save_record was finished
        self.statusBrowser.append(u"檔案已儲存，清空記憶體")
        self.statusBrowser.append("===== End Section =====")
        self.saveButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)

    # show stable checkbox option
    def enable_stable(self):
        check_stable = QMessageBox.question(self, u'啟動即時寫入', \
                                            u"此選項將延遲每筆資料速度，並保證資料即時記錄於檔案中，確定嗎？\n    按'Yes'啟動即時檔案寫入，\n    按'NO'取消即時檔案寫入", \
                                            QMessageBox.Yes | QMessageBox.No)

        if check_stable == QMessageBox.Yes:
            self.statusBrowser.append(u"*IMU即時寫入已啟動")
            self.stableCheckBox.setCheckState(2)
            self.saveButton.setEnabled(False)
        else:
            self.statusBrowser.append(u"*取消即時寫入")
            self.stableCheckBox.setCheckState(0)
            self.saveButton.setEnabled(True)


    #===== Picamera Func. area =====
    def preview(self):
        camera.stop_preview()
        if not self.preview_switch:
            self.camBrowser.append("Preview on.")
            camera.start_preview(fullscreen = False, window = (450, 10, 400, 300) )
            self.preview_switch = True
        elif self.preview_switch:
            self.camBrowser.append("Preview off.")
            self.camBrowser.append("==========")
            camera.stop_preview()
            self.preview_switch = False
        else:
            self.camBrowser.append("Prview Booom!")

    def film(self):
        #camera.stop_recording()
        film_path = self.path
        if not os.path.exists(film_path):
            try:
                os.makedirs(film_path)
            except OSError:
                if not os.path.isdir(film_path):
                    raise


        if not self.film_switch:
            self.camBrowser.append("Start Filming...")
            self.video_count += 1
            camera.start_recording(film_path + '/video%d.h264' %(self.video_count) )
            self.film_switch = True
            self.photoButton.setEnabled(False)

        elif self.film_switch:
            self.camBrowser.append("Stop Filming...")
            camera.stop_recording()
            self.camBrowser.append("Film saved.")
            self.film_switch = False
            self.camBrowser.append("==========")
            self.photoButton.setEnabled(True)
        else:
            self.camBrowser.append("Film Booom!")

    def take_photo(self):
        self.photo_count += 1
        self.filmButton.setEnabled(False)
        self.photoButton.setEnabled(False)

        # Create "Photo" folder if not exist
        photo_path = self.path
        if not os.path.exists(photo_path):
            try:
                os.makedirs(photo_path)
            except OSError:
                if not os.path.isdir(photo_path):
                    raise


        camera.capture(photo_path + '/image%d.jpg' %self.photo_count )
        self.camBrowser.append("image%d saved" %self.photo_count )

        self.photoButton.setEnabled(True)
        self.filmButton.setEnabled(True)


class imu_start_record(QThread):
    def  __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.stoped = False
        self.mutex = QMutex()
        #===== QTimer =====
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.connect(self.timer, SIGNAL("timeout()"), self.mpu9250_data_get_and_write)

    def run(self):
        global raw_data

        # varibles
        self.t0 = time.time()
        self.t_a_g = []

        with QMutexLocker(self.mutex):
            self.stoped = False
        self.timer.start()

        raw_data = list(self.t_a_g)
        #print "data copy!"

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stoped = True

    def isStop(self):
        with QMutexLocker(self.mutex):
            return self.stoped


    def mpu9250_data_get_and_write(self):

        # keep AKM pointer on continue measuring
        i2c.write_byte_data(0x0c, 0x0a, 0x16)

        # get MPU9250 smbus block data
        #xyz_g_offset = i2c.read_i2c_block_data(addr, 0x13, 6)
        xyz_a_out = i2c.read_i2c_block_data(addr, 0x3B, 6)
        xyz_g_out = i2c.read_i2c_block_data(addr, 0x43, 6)
        #xyz_a_offset = i2c.read_i2c_block_data(addr, 0x77, 6)

        # get AK8963 smbus data (by pass-through way)
        xyz_mag  = i2c.read_i2c_block_data(0x0c, 0x03, 6)
        #xyz_mag_adj = i2c.read_i2c_block_data(0x0c, 0x10, 3)

        # get real time
        t1 = time.time() - self.t0

        # save file to list buffer
        self.t_a_g.append(t1)
        self.t_a_g.append(xyz_a_out)
        self.t_a_g.append(xyz_g_out)
        self.t_a_g.append(xyz_mag)
        #self.t_a_g.append(xyz_mag_adj)
        time.sleep(0.00001)


class imu_start_record_stable(QThread):
    def  __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.stoped = False
        self.mutex = QMutex()
        self.t0 = time.time()
        self.imu_count_stable = 0

        self.countdown_sec = 60

        #===== QTimer =====
        self.big_timer = QTimer()
        self.timer = QTimer()
        #self.timer.setInterval(10)
        self.connect(self.timer, SIGNAL("timeout()"), self.mpu9250_data_get_and_write)



    def run(self):
        self.timer.start(7)
        self.big_timer.singleShot(self.countdown_sec *1000, self.stop)

        with QMutexLocker(self.mutex):
            self.stoped = False


    def stop(self):
        with QMutexLocker(self.mutex):
            self.stoped = True
            self.timer.stop()
            print 'Done'

    def isStop(self):
        with QMutexLocker(self.mutex):
            return self.stoped


    def mpu9250_data_get_and_write(self):
        # keep AKM pointer on continue measuring
        i2c.write_byte_data(0x0c, 0x0a, 0x16)

        # get MPU9250 smbus block data
        #xyz_g_offset = i2c.read_i2c_block_data(addr, 0x13, 6)
        xyz_a_out = i2c.read_i2c_block_data(addr, 0x3B, 6)
        xyz_g_out = i2c.read_i2c_block_data(addr, 0x43, 6)
        #xyz_a_offset = i2c.read_i2c_block_data(addr, 0x77, 6)

        # get AK8963 smbus data (by pass-through way)
        xyz_mag  = i2c.read_i2c_block_data(0x0c, 0x03, 6)
        #xyz_mag_adj = i2c.read_i2c_block_data(0x0c, 0x10, 3)

        # get real time
        t1 = time.time() - self.t0

        filename = "IMU_LOG_REALTIME_%s.txt" %(self.imu_count_stable)

        file_s = open(filename, "a")

        print >> file_s, "%.6f" %t1
        print >> file_s, xyz_a_out
        print >> file_s, xyz_g_out
        print >> file_s, xyz_mag
        file_s.close()
        time.sleep(0.00001)


class save_record(QThread):
    def  __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.imu_count = 0

    def run(self):
        global raw_data
        self.imu_count += 1

        try:
            filename = "IMU_LOG_%s.txt" %(self.imu_count)
            self.data_f = open(filename, "w")
            for i in raw_data:
                if isinstance(i, float):
                    print >> self.data_f ,"%f" %i
                else:
                    print >> self.data_f , i
        except:
            print "Data saving failed"

        finally:
            raw_data = []
            self.data_f.close()



if __name__ == "__main__":
	app=QApplication(sys.argv)
	IMU_GUI = IMU_GUI()
	IMU_GUI.show()
	sys.exit(app.exec_())
