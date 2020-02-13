import time

device_file = []
device_file.append('/sys/bus/w1/devices/28-021316a0f9aa/w1_slave')

def main():
    result = []

    for i in device_file:
        f = open(i, 'r')
        lines = f.readlines()
        f.close()

        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(id)

	equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            result.append(temp_c)
	    print(result[0])
        else:
            result.append('-')

    #f = open('sensorData','w')
    #f.write(";".join(map(str,result)))
    #f.close()


if __name__ == "__main__":
    main()
