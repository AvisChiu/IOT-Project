# https://blog.csdn.net/yannanxiu/article/details/51735452
import socket
import threading
import socketserver
import time
from queue import *
import json
import database as db


#client_addr = []
#client_socket = []

HOST, PORT = "0.0.0.0", 10023

clientDict={} # client_address:client_socket

#try merge this two dict
deviceDict={} # uuid:client_address >>> connect device dict
#deviceObjDict={} # uuid:device_object >>> all device dict



receiveQueue = Queue()	

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

	ip = ""
	port = 0
	timeOut = 6	 												# 设置超时时间变量
	deviceIsSetuped=False
	deviceUUID=""

	databaseConnect=db.DatabaseConnect()
	
	def setup(self):
		self.ip = self.client_address[0].strip()	 						# 获取客户端的ip
		self.port = self.client_address[1]		   							# 获取客户端的port
		self.request.settimeout(self.timeOut)									# 对socket设置超时时间
		print("[INFO]	"+self.ip+":"+str(self.port)+"连接到服务器！")
		
		#client_addr.append(self.client_address) 								# 保存到队列中
		#client_socket.append(self.request)	  								# 保存套接字socket
		
		clientDict[self.client_address]=self.request
		

	def setupDevice(self,uuid):
		self.deviceIsSetuped=True
		self.deviceUUID=uuid
		
		# load device object from database, refresh data
		self.databaseConnect.start()
		
		if deviceDict.get(uuid) == None:
			#device not exist, create device
			print("[DEV]	NEW DEVICE "+str(uuid))
			self.databaseConnect.createDevice(uuid)
			
		deviceDict[uuid]=self.databaseConnect.getDevice(uuid)
		self.databaseConnect.close()
		
		deviceDict[uuid]["socket"]=self.client_address
		
		print("[DEV]	DEVICE "+str(uuid)+" CONNECTED")
	
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
				
				
				#process jsonData
				if self.deviceIsSetuped:
					if jsonData.get('tag') == "hello":
						#hello data, update device info
						print("[DEV]	HELLO "+str(jsonData))
						deviceDict[self.deviceUUID]['info']=jsonData.get('data')
						print("[DEV]	"+str(deviceDict))
					else:
						#regular data, push to recv queue
						receiveDict = {'uuid': self.deviceUUID, 'data': jsonData} #should save uuid to queue?
						receiveQueue.put(receiveDict)
					
				else:
					#check if data is uuid
					if jsonData.get('uuid'):
						self.setupDevice(jsonData['uuid'])
						
					else:
						#if not, request uuid
						responseData={'info':'uuid'}
						self.request.sendall(json.dumps(responseData).encode('utf-8'))
						

	def finish(self):

		if self.deviceIsSetuped:
			deviceDict[self.deviceUUID]['socket']=None
			print("[DEV]	DEVICE "+str(self.deviceUUID)+" DISCONNECTED")
		del(clientDict[self.client_address])
		
		print("[INFO]	"+self.ip+":"+str(self.port)+"断开连接！")
		print("[DEV]	"+str(deviceDict))
		


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass


class RecvData():

	databaseConnect=db.DatabaseConnect()

	def work(self):
		self.databaseConnect.start()
		while True:

			receiveDict = receiveQueue.get()

			#{'uuid': self.deviceUUID, 'data': jsonData}
			recvUUID=receiveDict['uuid']
			recvData=receiveDict['data']
			
			print("[DATA]	RECV FROM "+recvUUID+" "+str(recvData))
			
			if recvData.get('tag'):
				self.databaseConnect.insertData(recvUUID,recvData)
			
			deviceAddress=deviceDict.get(recvUUID).get("socket")
			deviceSocket=clientDict.get(deviceAddress)
			
			
			if deviceSocket:
				#print("[DATA]	RESPONSE SENDED")
				try:
					deviceSocket.sendall(json.dumps({'info':'ok'}).encode('utf-8'))
				except:
					pass
			
			receiveQueue.task_done()
		
		databaseConnect.close()


class SocketThread():
	
	
	server = None
	server_thread = None
	option_1 = None
	server_thread_option_1 = None
	
	databaseConnect=db.DatabaseConnect()
	
	
	def __init__(self,port):
		global PORT
		global deviceDict
		PORT=port
		self.databaseConnect.start()
		deviceDict=self.databaseConnect.getAllDevice()
		#deviceObjDict=self.databaseConnect.getAllDevice()
		print("DEV	"+str(deviceDict))
		self.databaseConnect.close()
	
	def start_thread(self):
		global HOST, PORT
		self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.daemon = True												# Thread1: connect
		self.server_thread.start()
		print("[SERVER] Server loop running in thread:", self.server_thread.name)

		
		self.option_1 = RecvData()
		self.server_thread_option_1 = threading.Thread(target=self.option_1.work)		
		self.server_thread_option_1.daemon = True
		self.server_thread_option_1.start()

	def stop_thread(self):
		self.server.shutdown()
		self.server.server_close()
		
		
	def get_client(self):
		return clientDict
		
	def get_device(self):
		return deviceDict
		
	def get_device_by_level(self,level):
		returnDict=dict()
		for key, value in deviceDict.items():
			if value['level']>=level:
				returnDict[key]=value
				
		return returnDict
	
	def send_data_by_uuid(self,uuid,data):
		device=deviceDict.get(uuid)
		if device != None:
			device_address = device.get('socket')
			if device_address != None:
				socket = clientDict.get(device_address)
				if socket !=None:
					socket.sendall(json.dumps(data).encode('utf-8'))
					return True
					
		return False
		
	def send_config_to_device(self,uuid,config):
		return self.send_data_by_uuid(uuid,{"conf":config})
	
	#def get_all_device(self):
	#	return deviceObjDict
	
if __name__ == "__main__":
	pass