import socket
import time
import threading
from queue import *
import random

ip="127.0.0.1"
port=10023

sendQueue=Queue()
receiveQueue=Queue()


class ConnectThread(threading.Thread):
	
	daemon = True
	
	def run(self):
		sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		
		try:
			sk.connect((ip,port))
		except:
			print("CONNECTION ERROR")
			return
		
		while True:
			try:
				sendData=sendQueue.get_nowait()
				sk.sendall((sendData).encode("utf8"))
			except Empty:
				pass
			except:
				print("SEND ERROR EXCEPT")
				return
			else:
				sendQueue.task_done()
			
			try:
				data = sk.recv(1024)
			except ConnectionAbortedError:
				print("CONNECTION ABORTED ERROR")
				return
			except ConnectionResetError:
				print("CONNECTION RESETED")
				return
			else:
				if data:
					receiveQueue.put(data)
			
	

		
if __name__ == "__main__":
	
	
	connectThread = ConnectThread()
	connectThread.start()

	i=0
	
	while True:
	
		if(not connectThread.isAlive()):
			connectThread = ConnectThread()
			connectThread.start()
			continue
		
		if i<5 or i>10:
			sendQueue.put("Hello Server")
		i=i+1
		
		try:
			receiveData=receiveQueue.get_nowait()
		except Empty:
			pass
		else:
			print(receiveData.decode('UTF-8', 'ignore'))
			receiveQueue.task_done()
 
		time.sleep(1)
