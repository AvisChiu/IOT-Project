# https://blog.csdn.net/yannanxiu/article/details/51735452
import socket
import threading
import socketserver
import time
from queue import *
import json


#client_addr = []
#client_socket = []

clientDict={} #client_address:client_socket
deviceDict={} #uuid:client_address

receiveQueue = Queue()	

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

	ip = ""
	port = 0
	timeOut = 6	 												# 设置超时时间变量
	deviceIsSetuped=False
	deviceUUID=""

	def setup(self):
		self.ip = self.client_address[0].strip()	 						# 获取客户端的ip
		self.port = self.client_address[1]		   							# 获取客户端的port
		self.request.settimeout(self.timeOut)									# 对socket设置超时时间
		print(self.ip+":"+str(self.port)+"连接到服务器！")
		
		#client_addr.append(self.client_address) 								# 保存到队列中
		#client_socket.append(self.request)	  								# 保存套接字socket
		
		clientDict[self.client_address]=self.request
		

	def setupDevice(self,uuid):
		self.deviceIsSetuped=True
		self.deviceUUID=uuid
		deviceDict[uuid]=self.client_address
	
	def handle(self):
		recvData=''
		while True:												# while循环
			try:
				recvData+=self.request.recv(1024).decode('utf-8')
				#data = str(self.request.recv(1024), 'utf-8')
				
			except socket.timeout:  									# 如果接收超时会抛出socket.timeout异常
				print(self.ip+":"+str(self.port)+"接收超时！即将断开连接！")
				break   										# 记得跳出while循环
				
			except Exception as e:
				print(e)
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
					receiveDict = {'uuid': self.deviceUUID, 'data': jsonData} #should save uuid to queue?
					receiveQueue.put(receiveDict)
					
				else:
					#check if data is uuid
					if jsonData.get('uuid'):
						self.setupDevice(jsonData['uuid'])
						
					else:
						#if not, request uuid
						responseData={'info':'uuid'}
						self.request.sendall(json.dumps(responseData).encode())
						

	def finish(self):
		print(self.ip+":"+str(self.port)+"断开连接！")
		#client_addr.remove(self.client_address)
		#client_socket.remove(self.request)
		if self.deviceIsSetuped:
			deviceDict[self.deviceUUID]=None
		del(clientDict[self.client_address])
		


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass


class RecvData():

	def work(self):

		while True:

			receiveDict = receiveQueue.get()

			#{'uuid': self.deviceUUID, 'data': jsonData}
			recvUUID=receiveDict['uuid']
			recvData=receiveDict['data']
			
			print("RECEIVE DATA FROM "+recvUUID+" DATA "+str(recvData))
			
			deviceAddress=deviceDict.get(recvUUID)
			deviceSocket=clientDict.get(deviceAddress)
			
			if deviceSocket:
				print("RESP")
				deviceSocket.sendall("OK".encode('utf-8'))
			#try:
				#clientSocket.sendall(responseData)
			#except:
				#pass
			
				
			receiveQueue.task_done()

			#time.sleep(2)


if __name__ == "__main__":

	

	# Port 0 means to select an arbitrary unused port
	HOST, PORT = "localhost", 10023
	# Start a thread with the server -- that thread will then start one
	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

	#=======================================================================#

	# more thread for each request
	server_thread = threading.Thread(target=server.serve_forever)
	# Exit the server thread when the main thread terminates
	server_thread.daemon = True												# Thread1: connect
	server_thread.start()
	print("Server loop running in thread:", server_thread.name)

	#=======================================================================#

	option_1 = RecvData()
	server_thread_option_1 = threading.Thread(
		target=option_1.work)			# Thread2: option 1: recv data
	server_thread_option_1.daemon = True
	server_thread_option_1.start()

	#=======================================================================#

	while True:
		print("\nClient "+str(clientDict.keys()))
		print("\nDevice "+str(deviceDict))
		time.sleep(2)
		
	server.shutdown()
	server.server_close()