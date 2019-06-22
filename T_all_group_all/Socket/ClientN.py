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
		uuidData=json.dumps({'uuid':UUID})
		self.sendData(uuidData)
		
		return True
		
	def closeConnect(self):
		global clientSocket
	
		self.connectSocket.close()
		self.connectStatus=False
		clientSocket=None
		
	def sendData(self,data):
		#input string data
		try:
			self.connectSocket.sendall(data.encode("utf8"))
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
				print("SEND TO SERVER "+jsonData)
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
				sendQueue.put(json.dumps({'info':'heartbeat'}))
				
			time.sleep(3)
				
	
class RecvThread(threading.Thread):
	
	daemon = True

	def run(self):
		global clientSocket
	
		while True:
			
			if clientSocket==None:		
				time.sleep(1)
			
			else:
				try:
					recvData = clientSocket.recv(1024)
				except Exception as e:
					#print(e)
					clientSocket=None
					#let connectThread know if error?
					
				else:
					if recvData:
						receiveQueue.put(recvData)
						
				
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
			sendQueue.put(json.dumps(sendData))
		i=i+1
		
		try:
			receiveData=receiveQueue.get_nowait()
		except Empty:
			pass
		else:
			print(receiveData.decode('UTF-8', 'ignore'))
			receiveQueue.task_done()
 
		time.sleep(1)
