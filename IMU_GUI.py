#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author : MikeChan
# Email  : m7807031@gmail.com
# Date   : 05/30/2016

import smbus, picamera
import time, sys,threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *


#===== for raspberry PI =====
import smbus
import picamera
i2c = smbus.SMBus(1)
camera = picamera.PiCamera()
addr = 0x68
raw_data = []

#===== initial zone =====
try:
    device_id = i2c.read_byte_data(addr,0x75)
    print "Device ID:" + str(hex(device_id))
    print "MPU9250 I2C Connected."
    print ""
except:
    print "Connect failed"
    print ""

i2c.write_byte_data(0x68, 0x6a, 0x00)
i2c.write_byte_data(0x68, 0x37, 0x02)
i2c.write_byte_data(0x0c, 0x0a, 0x16)
#===== end initial ======


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
        self.resize(300,200)
        self.move(100,100)
        self.setWindowTitle("MPU9250 & PiCamera GUI")

        # varibles
        self.camera_switch = False

    def createLayout(self):
        self.camBrowser  = QTextBrowser()
        h4 = QHBoxLayout()
        h4.addWidget(self.camBrowser)

        self.previewButton = QPushButton("Preview")
        self.filmButton = QPushButton("Film")
        self.save_filmButton = QPushButton("Save Film")
        h5 = QHBoxLayout()
        h5.addWidget(self.previewButton)
        h5.addWidget(self.filmButton)
        h5.addWidget(self.save_filmButton)


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

        self.spaceLine = QLineEdit()
        h3 = QHBoxLayout()
        h3.addWidget(self.spaceLine)


        layout = QVBoxLayout()
        layout.addLayout(h4)
        layout.addLayout(h5)
        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addLayout(h3)

        self.setLayout(layout)


        self.previewButton.setEnabled(True)
        self.filmButton.setEnabled(True)
        self.save_filmButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.saveButton.setEnabled(False)

    def createConnection(self):
        #===== Picamera related =====
        self.previewButton.clicked.connect(self.preview)
        self.fileButton.clicked.connect(self.film)
        self.save_filmButton.clicked.connect(self.save_film)

        #===== IMU related =====
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.saveButton.clicked.connect(self.save)
        self.connect(self.save_record, SIGNAL("finished()"), self.finished)


    #===== IMU Func. area =====
    def start(self):
        self.tt0 = time.time()
        self.statusBrowser.append("Start Recording....")
        self.imu_start_record.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.saveButton.setEnabled(False)

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
        if not self.camera_switch:
            camera.start_preview(fullscreen = False, window = (350, 250, 400, 300) )
            self.camera_switch = True
        elif self.camera_switch:
            camera.stop_preview()
            self.camera_switch = False
        else:
            self.camBrowser.append("Blob!")

    def film(self):
        pass


    def save_film(self):
        pass



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


    def run(self):
        global raw_data

        try:
            self.data_f = open("IMU_LOG.txt", "w")
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
