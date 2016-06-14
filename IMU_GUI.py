#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author : MikeChan
# Email  : m7807031@gmail.com
# Date   : 06/14/2016

import smbus, picamera
import time, sys, os, datetime, threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *


#===== for raspberry PI =====
import smbus
import picamera
i2c = smbus.SMBus(1)
camera = picamera.PiCamera()
addr = 0x68
raw_data = []



#====== QT area ======
class IMU_GUI(QWidget):
    def __init__(self, parent = None):
        super(IMU_GUI, self).__init__(parent)
        self.imu_start_record = imu_start_record()
        self.save_record = save_record()

        # create Layout and connection
        self.createLayout()
        self.createConnection()

        # window properties adjustment
        self.resize(300,400)
        self.move(0,35)
        self.setWindowTitle("MPU9250 & PiCamera GUI")

        # varibles
        self.preview_switch = False
        self.film_switch = False
        self.IMU_KEY = False

        self.photo_count = 0
        self.video_count = 0
        self.now = datetime.datetime.now()

    def createLayout(self):
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


        self.statusBrowser  = QTextBrowser()
        h1 = QHBoxLayout()
        h1.addWidget(self.statusBrowser)

        self.startButton = QPushButton("Start IMU")
        self.stopButton = QPushButton("Stop IMU")
        self.saveButton = QPushButton("Save Data")
        h2 = QHBoxLayout()
        h2.addWidget(self.startButton)
        h2.addWidget(self.stopButton)
        h2.addWidget(self.saveButton)



        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout0 = QVBoxLayout()


        layout1.addLayout(h1)
        layout1.addLayout(h2)


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
        #===== Picamera related =====
        self.previewButton.clicked.connect(self.preview)
        self.filmButton.clicked.connect(self.film)
        self.photoButton.clicked.connect(self.take_photo)

        #===== IMU related =====
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.saveButton.clicked.connect(self.save)
        self.connect(self.save_record, SIGNAL("finished()"), self.finished)


    #===== IMU Func. area =====
    def start(self):
        # IMU initial
        self.statusBrowser.append("IMU Initializing...")

        try:
            i2c.write_byte_data(0x68, 0x6a, 0x00)
            i2c.write_byte_data(0x68, 0x37, 0x02)
            i2c.write_byte_data(0x0c, 0x0a, 0x16)
            self.statusBrowser.append("Initialization Done!")
            self.IMU_KEY = True

        except:
            self.statusBrowser.append("Initial Failed! Check Wiring...")
            self.IMU_KEY = False

            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.saveButton.setEnabled(False)
            #===== end initial ======

        if self.IMU_KEY:
            self.tt0 = time.time()
            self.statusBrowser.append("Start Recording....")
            self.imu_start_record.start()
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)
            self.saveButton.setEnabled(False)
        else:
            pass


    def stop(self):
        global raw_data

        self.duringTime = time.time() - self.tt0
        self.imu_start_record.stop()
        self.statusBrowser.append("Record Stop!")
        self.statusBrowser.append("During Time: " + "%.2f" %self.duringTime)

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.saveButton.setEnabled(True)

    def save(self):
        self.statusBrowser.append("Data saving....")
        time.sleep(1)
        self.save_record.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.saveButton.setEnabled(False)

    def finished(self):     # will be call when save_record was finished
        self.statusBrowser.append("Data saved, List and Port clear.")
        self.statusBrowser.append("===== End Section=====")
        self.saveButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)


    #===== Picamera Func. area =====
    def preview(self):
        camera.stop_preview()
        if not self.preview_switch:
            self.camBrowser.append("Preview on.")
            camera.start_preview(fullscreen = False, window = (400, 10, 400, 300) )
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
        if not self.film_switch:
            self.camBrowser.append("Start Filming...")
            self.video_count += 1
            camera.start_recording('video_%2d.h264' %self.video_count)
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
        photo_path = "photo"
        if not os.path.exists(photo_path):
            try:
                os.makedirs(photo_path)
            except OSError:
                if not os.path.isdir(photo_path):
                    raise


        camera.capture(photo_path + '/image_%2d.jpg' %self.photo_count)
        self.camBrowser.append("image_%2d saved" %self.photo_count)
        time.sleep(0.3)

        self.photoButton.setEnabled(True)
        self.filmButton.setEnabled(True)

class imu_start_record(QThread):
    def  __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.stoped = False
        self.mutex = QMutex()

    def run(self):
        global raw_data

        # varibles
        self.t_a_g = []
        self.t0 = time.time()

        with QMutexLocker(self.mutex):
            self.stoped = False

        while 1:
            if not self.stoped:
                self.mpu9250_data_get_and_write()
            else:
                break

        raw_data = list(self.t_a_g)


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
        #t_a_g.append(xyz_mag_adj)


class save_record(QThread):
    def  __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.imu_count = 0

    def run(self):
        global raw_data
        self.imu_count += 1

        try:
            self.data_f = open("IMU_LOG_" + str(self.imu_count) + ".txt", "w")
            for i in raw_data:
                if isinstance(i, float):
                    print >> self.data_f ,"%f" %i
                else:
                    print >> self.data_f , i
        except:
            print "Data saving failed"

        finally:
            i2c.write_byte_data(addr, 0x6A, 0x07)
            raw_data = []
            self.data_f.close()


if __name__ == "__main__":
	app=QApplication(sys.argv)
	IMU_GUI = IMU_GUI()
	IMU_GUI.show()
	sys.exit(app.exec_())
