import socket
import time
import threading
from queue import *
import random
import json



sendQueue=Queue()
receiveQueue=Queue()

#test UUID
UUID="d5c93353-a7fb-472c-a9f6-dd8807cffdd0"
SERVER='127.0.0.1'
PORT=10001

clientSocket=None


class ConnectThread(threading.Thread):
	#INITIALIZE CONNECT AND SEND HEARTBEAT
	daemon = True
	connectStatus=False
	connectSocket=None
	
	def startConnect(self):
	
		global clientSocket
		
		try:
			self.connectSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.connectSocket.connect((SERVER,PORT))
		except Exception as e:
			print(e)
			return False
		
		self.connectStatus=True
		clientSocket=self.connectSocket
		uuidData={'uuid':UUID}
		self.sendData(uuidData)
		
		return True
		
	def closeConnect(self):
		global clientSocket
	
		self.connectSocket.close()
		self.connectStatus=False
		clientSocket=None
		
	def sendData(self,data):
		#input dict data
		try:
			self.connectSocket.sendall(json.dumps(data).encode("utf8"))
		except Exception as e:
			print(e)
			self.closeConnect()
			#self.connectSocket.close()
			#self.connectStatus=False;
			return False
			
		return True
	
	def run(self):
				
		while True:
			
			#check connect status
			#try send data if connected
			#try connect if disconnected
			if self.connectStatus==False:
				self.startConnect()
			
			else:
				jsonData=sendQueue.get()
				print("[DATA]	SEND TO SERVER "+str(jsonData))
				self.sendData(jsonData)
				sendQueue.task_done()
		
		#self.finish()

	
class HeartbeatThread(threading.Thread):
	daemon = True
	
	def run(self):
		global clientSocket
		global sendQueue
		
		while True:
			if clientSocket==None:		
				time.sleep(1)
				continue
			
			if sendQueue.empty():
				sendQueue.put({'info':'heartbeat'})
				
			time.sleep(3)
				
	
class RecvThread(threading.Thread):
	
	daemon = True

	def run(self):
		global clientSocket
		recvData=''
		while True:
			
			if clientSocket==None:		
				time.sleep(1)
			
			else:
				try:#shold try parse json here?
					recvData += clientSocket.recv(1024).decode('utf-8')
				except Exception as e:
					#print(e)
					clientSocket=None
					#let connectThread know if error?
				
				else:

					while len(recvData):
						try:
							jsonData, decodeIndex = json.JSONDecoder().raw_decode(recvData)
							recvData=recvData[decodeIndex:]
						except ValueError:
							recvData=''
							break
							
						receiveQueue.put(jsonData)
						

class ClientSocketThread():

	connectThread=None
	recvThread=None
	heartbeatThread=None
	
	#SERVER='127.0.0.1'
	#PORT='10001'
	#UUID="d5c93353-a7fb-472c-a9f6-dd8807cffdd0"
	
	def __init__(self,server,port,uuid):
		global SERVER, PORT, UUID
		#self.SERVER=server
		#self.PORT=port
		#self.UUID=uuid
		SERVER=server
		PORT=port
		UUID=uuid
		
		self.connectThread = ConnectThread()
		self.recvThread = RecvThread()
		self.heartbeatThread = HeartbeatThread()
		
	def start_thread(self):
		
		self.connectThread.start()
		self.recvThread.start()
		self.heartbeatThread.start()
		
	def stop_thread(self):
		pass
		
	def sendData(self,data):
		global sendQueue
		#data should be dict?
		sendQueue.put(data)
	

	def recvData(self):
		# make it blocking
		global receiveQueue
		receiveData=receiveQueue.get()
		receiveQueue.task_done()
		return receiveData
	
	def recvDataList(self):
		global receiveQueue
		resultList=[]
		while True:
			try:
				receiveData=receiveQueue.get_nowait()
				resultList.append(receiveData)
			except Empty:
				break
			else:
				#print(receiveData.decode('UTF-8', 'ignore'))
				receiveQueue.task_done()
		
		return resultList
						
if __name__ == "__main__":
	
	
	connectThread = ConnectThread()
	connectThread.start()
	
	recvThread = RecvThread()
	recvThread.start()
	
	heartbeatThread = HeartbeatThread()
	heartbeatThread.start()

	i=0
	
	while True:

		if i<5 or i>10:
			sendData={'data':'Hello Server '+str(i)}
			sendQueue.put(sendData)
		i=i+1
		
		try:
			receiveData=receiveQueue.get_nowait()
		except Empty:
			pass
		else:
			print(receiveData.decode('UTF-8', 'ignore'))
			receiveQueue.task_done()
 
		time.sleep(1)
