import smbus
import sched, time
from threading import Timer,Thread,Event
#import RPi.GPIO as GPIO

#====== Global varible ======
i2c = smbus.SMBus(1)
addr = 0x68
t0 = time.time()
t_a_g = []
#t_a_g_2 = []
#====== Global varible end =======

#====== initial zone ======
try:
	device_id = i2c.read_byte_data(addr,0x75)
	print "Device ID:" + str(hex(device_id))
	print "MPU9250 I2C Connected."
except:
	print "Connect failed"

i2c.write_byte_data(0x68, 0x6a, 0x00)
i2c.write_byte_data(0x68, 0x37, 0x02)
i2c.write_byte_data(0x0c, 0x0a, 0x16)
#====== intial done ======

# Open File
f = open("IMU_LOG_9axis.txt", "w")


# ====== define basic func. ======
def mpu9250_data_get_and_write():
	global t_a_g

	# keep AKM pointer on continue measuring
	#i2c.write_byte_data(0x0c, 0x0a, 0x16)


	# get MPU9250 smbus block data
	#xyz_g_offset = i2c.read_i2c_block_data(addr, 0x13, 6)
	xyz_a_out = i2c.read_i2c_block_data(addr, 0x3B, 6)
	xyz_g_out = i2c.read_i2c_block_data(addr, 0x43, 6)
	#xyz_a_offset = i2c.read_i2c_block_data(addr, 0x77, 6)

	# get AK8963 smbus data (by pass-through way)
	#xyz_mag  = i2c.read_i2c_block_data(0x0c, 0x03, 6)
	#xyz_mag_adj = i2c.read_i2c_block_data(0x0c, 0x10, 3)

	# get real time
	t1 = time.time()

	t_a_g.append(t1)
	t_a_g.append(xyz_a_out)
	t_a_g.append(xyz_g_out)



	'''
	print >> f, t1
	print >> f, xyz_a_out
	print >> f, xyz_a_offset
	print >> f, xyz_g_out
	print >> f, xyz_g_offset
	print >> f, xyz_mag
	print >> f, xyz_mag_adj
	'''

def tag_to_f():
	global t_a_g

	for i in t_a_g:
		if isinstance(i, float):
			print >> f ,"%f" %i
		else:
			print >> f , i
	t_a_g = []

def clear_i2c_and_close_file():
	i2c.write_byte_data(addr, 0x6A, 0x07)
	f.close()
# ====== func. end ======


#====== Use these solution to get data and write to file ======

# solution 1: while true
def while_true_method():
	count = 1
	while True:
		if count <= 5000:
			mpu9250_data_get_and_write()
			count += 1
			time.sleep(0.01)
		else:
			tag_to_f()
			clear_i2c_and_close_file()
			break
	print "Process Done"


# solution 2: thread (remember to change time interval and ctrl + c to stop process.)
def thread_method():
	# make a thread
	class Thread_Get_MPU9250():

	   def __init__(self, time, start_f):
	      self.time = time
	      self.start_f = start_f

	      self.thread = Timer(self.time ,self.handle_function)

	   def handle_function(self):
	      self.start_f()
	      self.thread = Timer(self.time, self.handle_function)
	      self.thread.start()

	   def start(self):
	      self.thread.start()

	   def cancel(self):
	      self.thread.cancel()

	# enable thread
	try:
		m = Thread_Get_MPU9250(0.1, mpu9250_data_get_and_write)
		m.start()

	except KeyboardInterrupt:
		m.cancel()
		clear_i2c_and_close_file()
		print "Keyboard Interrupted!"

def print_time():
	print time.time()

# solution 3 : sched
def sched_method():
	s = sched.scheduler(time.time, time.sleep)

	# set parameter ======
	imu_time = 60
	data_hz = 100
	once_write_num = 100
	#====== End ======

	data_interval = 1.0/ data_hz
	how_many_sec_to_write = int(once_write_num * data_interval)

	for i in range(imu_time * data_hz):
		s.enter( i * data_interval, 0, mpu9250_data_get_and_write, ())

	for j in range(0, imu_time, how_many_sec_to_write):
		s.enter(j, 1,tag_to_f, () )

	s.run()


#sched_method()
while_true_method()
clear_i2c_and_close_file()
