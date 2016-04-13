import smbus
import time,timeit
#import RPi.GPIO as GPIO

# Global varible
i2c = smbus.SMBus(1)
addr = 0x68

c_t0 = time.clock()
t_t0 = time.time()

try:
	device_id = i2c.read_byte_data(addr,0x75)
	print "Device ID:" + str(hex(device_id))
	print "MPU9250 I2C Connected."
except:
	print "Connect failed"


i2c.write_byte_data(0x68, 0x6a, 0x00)
i2c.write_byte_data(0x68, 0x37, 0x02)
i2c.write_byte_data(0x0c, 0x0a, 0x16)


# Open File
f = open("IMU_LOG_9axis.txt", "w")


# Loop area
def read_write_mpu9250():
	count = 1

	while True:
		if count <= 500:

			def smbus_data_get():
				i2c.write_byte_data(0x0c, 0x0a, 0x16)
				#temp_out = i2c.read_i2c_block_data(addr, 0x41, 2)
				xyz_g_offset = i2c.read_i2c_block_data(addr, 0x13, 6)
				xyz_a_out = i2c.read_i2c_block_data(addr, 0x3B, 6)
				xyz_g_out = i2c.read_i2c_block_data(addr, 0x43, 6)
				xyz_a_offset = i2c .read_i2c_block_data(addr, 0x77, 6)

				xyz_mag  = i2c.read_i2c_block_data(0x0c, 0x03, 6)

				c_t1 = time.clock() - c_t0
				t_t1 = time.time() - t_t0


			smbus_data_get()	

			print >> f, count
			print >> f, c_t1, t_t1
			print >> f, xyz_a_out
			print >> f, xyz_a_offset
			print >> f, xyz_g_out
			print >> f, xyz_g_offset
			print >> f, xyz_mag

			count += 1
		else:
			f.close()
			i2c.write_byte_data(addr, 0x6A, 0x07)
			break

print timeit.timeit(read_write_mpu9250, number = 1)
print "Process End"
