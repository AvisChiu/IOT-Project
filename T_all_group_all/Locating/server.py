import socketserver
import threading
import time
import socket
import json
import queue
import frssi
import numpy as np
import box
import kalman_locating as kl
import database
#import page

#flaskThread = page.FlaskThread(3)
#flaskThread.start()

db_connect = database.DatabaseConnect()
db_connect.start()

clientDict = {}
receiveQueue = queue.Queue()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

	ip = ""
	port = 0
	timeOut = 6	 												# 设置超时时间变量

	
	def setup(self):
		self.ip = self.client_address[0].strip()	 						# 获取客户端的ip
		self.port = self.client_address[1]		   							# 获取客户端的port
		self.request.settimeout(self.timeOut)									# 对socket设置超时时间
		print("[INFO]	"+self.ip+":"+str(self.port)+"连接到服务器！")		

		clientDict[self.client_address]=self.request
		

	
	def handle(self):
		recvData=''
		while True:												# while循环
			
			try:
				recvTemp=self.request.recv(1024)
				if recvTemp == b'':
					break
				recvData+=recvTemp.decode('utf-8')
				#data = str(self.request.recv(1024), 'utf-8')
				
			except socket.timeout:  									# 如果接收超时会抛出socket.timeout异常
				print("[INFO]	"+self.ip+":"+str(self.port)+"接收超时！即将断开连接！")
				break   										# 记得跳出while循环
				
			except Exception as e:
				print("[ERR]	"+str(e))
				break


			while len(recvData):											# 判断是否接收到数据
				
				try:
					jsonData, decodeIndex = json.JSONDecoder().raw_decode(recvData)
					recvData=recvData[decodeIndex:]
				except ValueError:
					recvData=''
					break
					
				#regular data, push to recv queue
				receiveDict = {'data': jsonData} #should save uuid to queue?
				receiveQueue.put(receiveDict)
					

						

	def finish(self):


		del(clientDict[self.client_address])
		
		print("[INFO]	"+self.ip+":"+str(self.port)+"断开连接！")
		


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass


stations = {
	# station 4
	'8C:3B:AD:22:02:66': {
		'x':	13.29,
		'y':	1.05,
		'z':	2.9,
		'signalAttenuation': 2,
		'reference': {
			'distance': 1,
			'signal': -20
		}
	},
	# station 2
	'00:11:32:9D:2B:30': {
		'x':	0.61,
		'y':	7.04,
		'z':	2.9,
		'signalAttenuation': 1.8,
		'reference': {
			'distance': 1,
			'signal': -20
		}
	},
	# 1 station
	'00:11:32:9D:30:3A': {
		'x':	0.82,
		'y':	-0.15,
		'z':	0,
		'signalAttenuation': 3.5,
		'reference': {
			'distance': 7.9,
			'signal': -46
		}
	},
	# station 3
	'8C:3B:AD:21:FF:66': {
		'x':	14.24,
		'y':	7.78,
		'z':	0,
		'signalAttenuation': 3.5,
		'reference': {
			'distance': 7.9,
			'signal': -46
		}
	},
}


	
HOST = "0.0.0.0"
PORT = 12345

server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True												# Thread1: connect
server_thread.start()
print("[SERVER] Server loop running in thread:", server_thread.name)



#flaskThread.set_data("quq")


rssi_localizer = frssi.RSSILocalizer(stations)


macs = ['8C:3B:AD:22:02:66','00:11:32:9D:2B:30','00:11:32:9D:30:3A','8C:3B:AD:21:FF:66']


signal_dict={}
dist_dict={}
dist_lock = threading.Lock()

for mac in macs:
	signal_dict[mac]=-35
	dist_dict[mac]=7

find_thread = threading.Thread(daemon=True,target=box.find_thread,args=(dist_dict,dist_lock,))

find_thread.start()

# port kl
kl_signal_list_dict={}
kl_f_signal_dict={}
for mac in macs:
	kl_signal_list_dict[mac]=[]
	kl_f_signal_dict[mac]=0

while True:
	#time.sleep(1)
	try:
		recvData = receiveQueue.get(timeout=1)
		rssi_data = recvData['data']
		print("	[RSSI]	" + str(rssi_data))	
		#for mac,signal in rssi_data.items():
		
		for mac,old_signal in signal_dict.items():
			new_signal = rssi_data.get(mac)
			if new_signal is None:
				new_signal = old_signal
			
			signal_dict[mac] = 0.8*old_signal+0.2*new_signal
			
		
		#print("[SSSI]	" + str(signal_dict))
		
		dist_lock.acquire()
		dist_dict.update(rssi_localizer.getDistanceFromAllAP(signal_dict))
		dist_lock.release()
		print("	[DIST]	"+str(dist_dict))
		
		# do kl
		
		# append data
		for mac,rssi in rssi_data.items():
			kl_signal_list_dict[mac].append(rssi)
			
			
		for mac,list in kl_signal_list_dict.items():
			if len(list) >= 5:
				kl_f_signal_dict[mac]=kl.go_filter(list)
				#clean list?
				
		
		# check data is enough
		kl_data_check = True
		for mac,signal in kl_f_signal_dict.items():
			if signal == 0:
				kl_data_check = False
		
		if kl_data_check:
			# data enough, do locating
			
			kl_dist_dict = rssi_localizer.getDistanceFromAllAP(kl_f_signal_dict)
			
			dist_ap4 = kl_dist_dict.get('8C:3B:AD:22:02:66')
			dist_ap2 = kl_dist_dict.get('00:11:32:9D:2B:30')
			dist_ap1 = kl_dist_dict.get('00:11:32:9D:30:3A')
			dist_ap3 = kl_dist_dict.get('8C:3B:AD:21:FF:66')
			
			kl_locaion = kl.Locating(dist_ap1,dist_ap2,dist_ap3,dist_ap4)
			print(" ")
			kl_loc = kl_locaion.lets_get_data()
			db_connect.add_loc(kl_loc[0],kl_loc[1],kl_loc[2],'kl')
			print(" ")
			for mac in macs:
				kl_signal_list_dict[mac]=[]
				kl_f_signal_dict[mac]=0
		
		
		receiveQueue.task_done()
	except queue.Empty:
		pass