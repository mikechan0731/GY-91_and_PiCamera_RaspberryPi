import smbus
import time
import RPi.GPIO as GPIO

# Global varible
i2c = smbus.SMBus(1)
addr = 0x68
count = 1
t0 = time.clock()

# check device connection by read device_id(should return 0x71)
try:
	device_id = i2c.read_byte_data(addr,0x75)
	print "Device ID:" + str(hex(device_id))
	print "MPU9250 I2C Connected."
except:
	print "Connect failed"

'''
# enable slave0 read-mode, from 0x00, read 9 byte to 0x49
i2c.write_byte_data(addr, 0x25, 0x8c)
i2c.write_byte_data(addr, 0x26, 0x00)
i2c.write_byte_data(addr, 0x27, 0x89)

# enable user master mode
i2c.write_byte_data(addr, 0x6a, 0x20)

# read 9 byte from 0x49 0x50....etc.
data1 = i2c.read_i2c_block_data(addr, 0x49, 10)

#print data1


# enable slave0 write-mode, target is 0x0a, write 1 byte)
i2c.write_byte_data(addr, 0x25, 0x0c)
i2c.write_byte_data(addr, 0x26, 0x0a)
i2c.write_byte_data(addr, 0x27, 0x81)

#enable user master mode
i2c.write_byte_data(addr, 0x6a, 0x20)

# throw 0x81 from 0x27 to 0x16 and transfer to 0x0a
i2c.write_byte_data(addr, 0x63, 0x16)


#disable write-mode and enable read-mode
i2c.write_byte_data(addr, 0x25, 0x8c)

#print i2c.read_byte_data(addr, 0x49)

i2c.write_byte_data(addr, 0x25, 0x8C)
i2c.write_byte_data(addr, 0x26, 0x03)
i2c.write_byte_data(addr, 0x27, 0x86)


real_data = i2c.read_i2c_block_data(addr, 0x49, 6)

print real_data
'''

i2c.write_byte_data(0x68, 0x6a, 0x00)
i2c.write_byte_data(0x68, 0x37, 0x02)
i2c.write_byte_data(0x0c, 0x0a, 0x16)

# Open File
f = open("IMU_LOG", "w")


# Loop area
while True:
	if count <= 5000:

		i2c.write_byte_data(0x0c, 0x0a, 0x16)

		#temp_out = i2c.read_i2c_block_data(addr, 0x41, 2)
		xyz_g_offset = i2c.read_i2c_block_data(addr, 0x13, 6)
		xyz_a_out = i2c.read_i2c_block_data(addr, 0x3B, 6)
		xyz_g_out = i2c.read_i2c_block_data(addr, 0x43, 6)
		xyz_a_offset = i2c .read_i2c_block_data(addr, 0x77, 6)

		xyz_mag  = i2c.read_i2c_block_data(addr, 0x49, 6)


		t1 =  time.clock() - t0

		print >> f, count
		print >> f, t1
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

print "Process End"



"""
print "xyz_g_out"
print xyz_g_out
print "xyz_g_offset"
print xyz_g_offset

print "xyz_a_out"
print xyz_a_out
print "xyz_a_offset"
print xyz_a_offset
"""
