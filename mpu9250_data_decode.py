import binascii as ba

f = open("IMU_LOG_9axix_keep_con.txt")
w = open("IMU_LOG_DECODE.txt", "w")

# transfer list to string seperate by "\t" ex: [1,2,3] -> "1    2   3   "
def list_sep(list_1):
    j = ""
    for i in list_1:
        j += str(i) + "\t"

    return j

# transfer 6 bytes list to 2bytes data ex: [255, 70, 66, 255, 20, 0] -> [ff46, 42ff, 1400] -> [65350, 17151, 578]
def list_2byte_hex2Dec(lis, MSB_or_LSB = "MSB"):
    """
    print ""
    print "You choose " + MSB_or_LSB + " hex code."
    print ""
    """
    MLSB = MSB_or_LSB

    all_hex = []
    for i in range(len(lis)):
        hex_done = hex(int(lis[i]))
        all_hex.append(str(hex_done))


    two_hex = []
    for m in range(len(all_hex)):
        if m % 2 == 0:
            a = str(all_hex[m].lstrip('0x'))
            b = str(all_hex[m+1].lstrip('0x'))

            if len(a) == 1:
                a = "0" + a
            elif len(a) == 0:
                a = "00"

            if len(b) == 1:
                b = "0" + b
            elif len(b) == 0 :
                b = "00"


            # check MSB or LSB
            if MLSB == "MSB":
                two_hex.append(a + b)
            elif MLSB == "LSB":
                two_hex.append(b + a)
            else:
                print "Error about MSB or LSB"
                break

    three_num = []
    for n in two_hex:
        byte2_hex_int = int(n, 16)
        if byte2_hex_int > 32768:
            byte2_hex_int -= 65535
        three_num.append(byte2_hex_int)

    return three_num


def str_to_list(st):
    i = st.strip("[]")
    j = i.split(", ")
    num_list = []
    for index in j:
        num_list.append(int(index))
    return num_list


def parse_all():

    #Give file header
    header = "count\ttime\tax\tay\taz\tax_off\tay_off\taz_off\tgx\tgy\tgz\tgx_off\tgy_off\tgz_off\tmagx\tmagy\tmagz"
    print >> w, header

    data_line_list = []
    data_list = []


    # save stripped data in list
    for data_line in f:
        data_line_strip = data_line.strip()
        data_line_list.append(data_line_strip)


    result_data = ""
    for i in range(len(data_line_list)):

        '''
        #check wrong data
        if i == 741 * 7:
            print data_line_list[i]
            print list_2byte_hex2Dec(str_to_list(data_line_list[i+4]))
            print list_2byte_hex2Dec(str_to_list(data_line_list[i+5]))
        '''

        if i % 7 == 0:
            try:
                axyz_list     = list_2byte_hex2Dec(str_to_list(data_line_list[i+2]))
                axyz_off_list = list_2byte_hex2Dec(str_to_list(data_line_list[i+3]))
                gxyz_list     = list_2byte_hex2Dec(str_to_list(data_line_list[i+4]))
                gxyz_off_list = list_2byte_hex2Dec(str_to_list(data_line_list[i+5]))
                magxyz_list   = list_2byte_hex2Dec(str_to_list(data_line_list[i+6]), "LSB")

                print >> w, data_line_list[i] +"\t" + data_line_list[i+1] + "\t" + list_sep(axyz_list) + list_sep(axyz_off_list) + list_sep(gxyz_list) + list_sep(gxyz_off_list) + list_sep(magxyz_list)
                 #+ list_sep(gxyz_list) + list_sep(gxyz_off_list)
            except:
                error_log = open("error_log.txt", "a")
                print >> error_log, "Count List for error index"
                print >> error_log, i / 7
                error_log.close()
                pass


#===== test code area ======
#write_count_time()
#print list_sep([27, 100, 0, 17, 106, 0])
parse_all()
#print list_2byte_hex2Dec([254, 144, 254, 212, 61, 112], "LSB")
#print str_to_list("[1, 2, 3]")


f.close()
w.close()
print "Program Done."
