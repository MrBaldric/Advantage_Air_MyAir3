import urllib2
import time
import psycopg2
from socket import *
#Version 1
#Polling AC unit for system data and zone data status
#IP address of AC unit manual stored in this program

#Version 2
#Added IPAddress enquiry script to start of program

##########################################
#Get IP address from AC Unit
UDP_IP = "192.168.1.1"
UDP_TXPORT = 3000
UDP_RXPORT = 3001
MESSAGE = "identify"
#Transmit enquiry to AC Unit
socktx = socket(AF_INET, SOCK_DGRAM)
socktx.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
socktx.sendto(MESSAGE, ('<broadcast>', UDP_TXPORT))

#Listen for enqiry response
sockrx = socket(AF_INET, SOCK_DGRAM)
sockrx.bind((UDP_IP, UDP_RXPORT))
#data is web page response, addr[0] is IP address and addr[1] is TX port number
data, addr = sockrx.recvfrom(1024)

#Get current time
currentDate = time.strftime("%b %d %Y",time.localtime((time.time())))
currentTime = time.strftime("%H:%M:%S",time.localtime((time.time())))
#login in to AC unit IP address from above using password
login_script = urllib2.urlopen("http://{}/login?password=password".format(addr[0])).read()	#carry out login to MyAir3
zoneNumber = 1
#setup connection to postgresql database
con = psycopg2.connect("dbname=<databasename> user=<username> password=<password>")
cur = con.cursor()
#get system data from AC unit
system_data_script = urllib2.urlopen("http://{}/getSystemData".format(addr[0])).read()
#Strip data out of response from AC Unit
acrssp = system_data_script.find('<airconOnOff>') + 13			#acrssp = A/C run status start point
acrsep = system_data_script.find('</airconOnOff>')				#acrsep = A/C run status end point
acfssp = system_data_script.find('<fanSpeed>') + 10				#acfssp = A/C fan speed start point
acfsep = system_data_script.find('</fanSpeed>')					#acfsep = A/C fan speed end point
acmsp = system_data_script.find('<mode>') + 6					#acmsp = A/C mode start point
acmep = system_data_script.find('</mode>')						#acmep = A/C mode end point

ac_run_status = system_data_script[acrssp:acrsep]
ac_speed_status = system_data_script[acfssp:acfsep]
ac_mode_status = system_data_script[acmsp:acmep]
#Update postgreSL database
cur.execute("UPDATE\
			system_data_current\
			SET\
			date_ = %s,\
			time_ = %s,\
			ac_on_off = %s,\
			fan_speed = %s,\
			temp_mode = %s\
			WHERE id = 1",(\
						currentDate,\
						currentTime,\
						ac_run_status,\
						ac_speed_status,\
						ac_mode_status\
						))
cur.execute("INSERT INTO\
			system_data_history(\
			date_,\
			time_,\
            ac_on_off,\
            fan_speed,\
            temp_mode)\
            VALUES(%s,%s,%s,%s,%s)",(\
							currentDate,\
							currentTime,\
							ac_run_status,\
							ac_speed_status,\
							ac_mode_status\
							))


if ac_run_status == '0':
	ac_run_status = "off"
else:
	ac_run_status = "on"
#Gather zone data from AC unit
while zoneNumber < 8:
	zone_data_script = urllib2.urlopen("http://{}/getZoneData?zone={}".format(addr[0],zoneNumber)).read()

	znsp = zone_data_script.find('<name>') + 6       			#znsp = zone name start point
	znep = zone_data_script.find('</name>')            			#znep = zone name end point
	zssp = zone_data_script.find('<setting>') + 9    			#zssp = zone setting start point
	zsep = zone_data_script.find('</setting>')          		#zsep = zone setting end point
	zatsp = zone_data_script.find('<actualTemp>') + 12			#zatsp = zone actual temp start point
	zatep = zone_data_script.find('</actualTemp>')        		#zatep = zone actual temp end point
	zdtsp = zone_data_script.find('<desiredTemp>') + 13   		#zdtsp = zone desired temp start point
	zdtep = zone_data_script.find('</desiredTemp>')    			#zdtep = zone desired temp end point

	zone_name = zone_data_script[znsp:znep]
	zone_setting = zone_data_script[zssp:zsep]
	zone_actualTemp = zone_data_script[zatsp:zatep]
	zone_desiredTemp = zone_data_script[zdtsp:zdtep]
	#Unpdate postgresql database
	cur.execute("UPDATE\
			zone_data_current\
			SET\
			date_ = %s,\
			time_ = %s,\
			zone_number = %s,\
			zone_name = %s,\
			zone_on_off = %s,\
			zone_actual_temp = %s,\
			zone_desired_temp = %s\
			WHERE id = %s",(\
						currentDate,\
						currentTime,\
						zoneNumber,\
						zone_name,\
						zone_setting,\
						zone_actualTemp,\
						zone_desiredTemp,\
						zoneNumber\
						))
	cur.execute("INSERT INTO\
			zone_data_history(\
			date_,\
			time_,\
            zone_number,\
            zone_name,\
            zone_on_off,\
            zone_actual_temp,\
            zone_desired_temp)\
            VALUES(%s,%s,%s,%s,%s,%s,%s)",(\
							currentDate,\
							currentTime,\
							zoneNumber,\
							zone_name,\
							zone_setting,\
							zone_actualTemp,\
							zone_desiredTemp,\
							))

    #Change zone setting to word off or on
	if zone_setting == '0':
		zone_setting = "off"
	else:
		zone_setting = "on"
#Increment zone number
	zoneNumber += 1

#Commit changes to postgresql database
con.commit()
#close connections to postgresql database
cur.close()
con.close()