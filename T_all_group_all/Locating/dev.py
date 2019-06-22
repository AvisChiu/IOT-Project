import socket
import threading
import time
import queue
import json
import frssi

UUID="d5c93353-a7fb-472c-a9f6-dd8807cffdd0"
SERVER='140.112.29.222'
PORT=12345

#clientSocket=None


class ConnectThread(threading.Thread):
	#INITIALIZE CONNECT AND SEND HEARTBEAT
	daemon = True
	connectStatus=False
	connectSocket=None
	sendQueue=queue.Queue()
	
	def startConnect(self):
	
		global clientSocket
		
		try:
			self.connectSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.connectSocket.connect((SERVER,PORT))
		except Exception as e:
			print(e)
			return False
		
		self.connectStatus=True
		#clientSocket=self.connectSocket
		#uuidData={'uuid':UUID}
		#self.sendData(uuidData)
		return True
		
	def closeConnect(self):
		#global clientSocket
	
		self.connectSocket.close()
		self.connectStatus=False
		#clientSocket=None
		
	def send(self,data):
		self.sendQueue.put(data)
		
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
				jsonData=self.sendQueue.get()
				print("[DATA]	SEND TO SERVER "+str(jsonData))
				self.sendData(jsonData)
				self.sendQueue.task_done()
				
connectThread = ConnectThread()
connectThread.start()

macs = ['8C:3B:AD:22:02:66','00:11:32:9D:2B:30','00:11:32:9D:30:3A','8C:3B:AD:21:FF:66','74:DA:38:E3:EA:4B','70:4F:57:DF:3D:3A','64:09:80:7B:D8:C5']

interface = 'wlp3s0'
rssi_scanner = frssi.RSSIScanner(interface)


while True:
	ap_info = rssi_scanner.getAPinfoByMAC(networks=macs, sudo=True)
	signal_data = {}
	if ap_info is not False:
		for ap in ap_info:
			signal_data[ap['mac']] = ap['signal']
	else:
		time.sleep(1)
	connectThread.send(signal_data)
	#time.sleep(1)
