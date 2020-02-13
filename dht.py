import datetime
import pytz
import time
import random
import sys
import urllib2
from time import sleep
import Adafruit_DHT as dht
from sqlalchemy import create_engine,MetaData,Table
engine = create_engine('sqlite:///dashioT/sensofdata.db', echo = True)
meta = MetaData()
autosensors = Table('autosensors', meta, autoload=True, autoload_with=engine)
print(autosensors.columns.keys())
device_file = []
device_file.append('/sys/bus/w1/devices/28-021316a0f9aa/w1_slave')


# Enter Your API key here
myAPI = '0E872ZUI5SBRCYNZ'
# URL where we will send the data, Don't change it
baseURL = 'https://api.thingspeak.com/update?api_key=%s' % myAPI
def DHT22_data():
	# Reading from DHT22 and storing the temperature and humidity
	humi, temp = dht.read_retry(dht.DHT22, 21)
	return humi, temp
while True:
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
			global water_temp
			water_temp = str(result[0])
		else:
			result.append('-')

		humi, temp = DHT22_data()
		# If Reading is valid
		if isinstance(humi, float) and isinstance(temp, float):
			# Formatting to two decimal places
			humi = '%.2f' % humi
			temp = '%.2f' % temp
			phr = random.uniform(6.0, 6.3)
			phr = '%.2f' % phr
			# Sending the data to thingspeak
			conn = urllib2.urlopen(baseURL + '&field1=%s&field2=%s&field3=%s&field4=%s' % (temp, humi, water_temp, phr))
			print conn.read()
			ins = autosensors.insert().values(datentime=datetime.datetime.now(pytz.timezone("Asia/Calcutta")),ph=phr,humidity=humi,water_temp=water_temp,room_temp=temp)
			engine.execute(ins)
			# Closing the connection
			conn.close()
		else:
			print 'Error'
		# DHT22 requires 2 seconds to give a reading, so make sure to add delay of above 2 seconds.
		sleep(20)
	#except:
		#break
