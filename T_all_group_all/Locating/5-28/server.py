import socketserver
import threading
import time
import socket
import json
import queue
import frssi

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
	'8C:3B:AD:22:02:66': {
		'x':	13.29,
		'y':	1.05,
		'z':	2.9
	},
	'00:11:32:9D:2B:30': {
		'x':	0.61,
		'y':	7.04,
		'z':	2.9
	},
	'00:11:32:9D:30:3A': {
		'x':	0.82,
		'y':	-0.15,
		'z':	0
	},
	'8C:3B:AD:21:FF:66': {
		'x':	14.24,
		'y':	7.78,
		'z':	0
	},
}

	
HOST = "0.0.0.0"
PORT = 12345
server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True												# Thread1: connect
server_thread.start()
print("[SERVER] Server loop running in thread:", server_thread.name)
rssi_localizer = frssi.RSSILocalizer(stations)

data_ap1 = []
data_ap2 = []
data_ap3 = []
data_ap4 = []

# while True:
# 	#time.sleep(1)
# 	try:
# 		recvData = receiveQueue.get(timeout=1)
# 		print("[RSSI]	" + str(recvData['data']))
# 		m = str(rssi_localizer.getDistanceFromAllAP(recvData['data']))
# 		print("[DIST]	"+ m )
# 		receiveQueue.task_done()

# 	except queue.Empty:
# 		pass


while True:
	#time.sleep(1)
	try:
		recvData = receiveQueue.get(timeout=1)
		# qq = str(recvData['data'])
		# print("[RSSI]	" + str(recvData['data']))
		# qq = float(qq[22:25])

		if len(recvData['data']) == 4:
			
			


			# ap1 = recvData['data']['00:11:32:9D:30:3A']
			# ap2 = recvData['data']['00:11:32:9D:2B:30']
			# ap3 = recvData['data']['8C:3B:AD:21:FF:66']
			# ap4 = recvData['data']['8C:3B:AD:22:02:66']
			# distance_ap1 = str(rssi_localizer.getDistanceFromAP1(ap1))
			# distance_ap2 = str(rssi_localizer.getDistanceFromAP2(ap2))
			# distance_ap3 = str(rssi_localizer.getDistanceFromAP3(ap3))
			# distance_ap4 = str(rssi_localizer.getDistanceFromAP4(ap4))
		
		
		
			ap1 = recvData['data']['2E:0E:3D:6E:5C:DF']
			ap2 = recvData['data']['C2:C2:EA:DF:DE:7A']
			distance_ap1 = str(rssi_localizer.getDistanceFromAP1(ap1))
			distance_ap2 = str(rssi_localizer.getDistanceFromAP2(ap2))

			

			print(ap1)
			print(ap2)
			print(distance_ap1)
			print(distance_ap2)
		
		


		receiveQueue.task_done()


		
	

		
	except queue.Empty:
		pass