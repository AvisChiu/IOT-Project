#!/usr/bin/python3

import io
import socket
import struct
import time
import picamera
import threading
import queue
import json


SERVER = '127.0.0.1'
IMAGE_PORT = 10037
COMMAND_PORT = 10040

class ImageThread(threading.Thread):

	SERVER = ''
	PORT = 0
	daemon = True
	
	client_socket = None
	
	def __init__(self, SERVER, PORT):
		threading.Thread.__init__(self)
		self.SERVER = SERVER
		self.PORT = PORT
		
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect((self.SERVER, self.PORT))
		self.connection = self.client_socket.makefile('wb')

	def run(self):
		try:
			with picamera.PiCamera() as camera:
				camera.resolution = (320, 240)	  # pi camera resolution
				camera.framerate = 15			   # 15 frames/sec
				time.sleep(2)					   # give 2 secs for camera to initilize
				self.start = time.time()
				self.stream = io.BytesIO()
				
				# send jpeg format video stream
				for foo in camera.capture_continuous(self.stream, 'jpeg', use_video_port = True):
					self.connection.write(struct.pack('<L', self.stream.tell()))
					self.connection.flush()
					self.stream.seek(0)
					self.connection.write(self.stream.read())
					#if time.time() - start > 600:
					#	break
					self.stream.seek(0)
					self.stream.truncate()
			self.connection.write(struct.pack('<L', 0))
		finally:
			self.connection.close()
			self.client_socket.close()

class CommandThread(threading.Thread):

	SERVER = ''
	PORT = 0

	daemon = True
	
	connectStatus=False
	connectSocket=None
	sendQueue=queue.Queue()
	receiveQueue = queue.Queue()
	receive_thread = None
	
	def __init__(self, SERVER, PORT):
		threading.Thread.__init__(self)
		self.SERVER = SERVER
		self.PORT = PORT
		self.receive_thread = threading.Thread(target=self.recvData, daemon=True)
		self.heartbeat_thread = threading.Thread(target=self.sendHeartbeat, daemon=True)
		self.startConnect()
		self.receive_thread.start()
		self.heartbeat_thread.start()
		#self.sendData({'test': 'hello'})
		
	
	def startConnect(self):
		try:
			self.connectSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.connectSocket.connect((self.SERVER,self.PORT))
		except Exception as e:
			print(e)
			return False
		
		self.connectStatus=True

		return True
		
	def closeConnect(self):	
		self.connectSocket.close()
		self.connectStatus=False

		
	def send(self,data):
		self.sendQueue.put(data)
		
	def sendData(self,data):
		#input dict data
		try:
			self.connectSocket.sendall(json.dumps(data).encode("utf8"))
		except Exception as e:
			print(e)
			self.closeConnect()

			return False
			
		return True
		
	def recvData(self):
		recvData=''
		while True:
			if self.connectSocket==None:		
				time.sleep(1)
				continue
			else:
				try:
					recvData += self.connectSocket.recv(1024).decode('utf-8')
				except Exception as e:
					print(e)
					self.closeConnect()
				else:
					while len(recvData):
						try:
							jsonData, decodeIndex = json.JSONDecoder().raw_decode(recvData)
							recvData=recvData[decodeIndex:]
						except ValueError:
							recvData=''
							break
						receiveQueue.put(jsonData)
	
	def sendHeartbeat(self):
		while True:
			if self.connectSocket==None:		
				time.sleep(1)
				continue
			
			if self.sendQueue.empty():
				self.sendQueue.put({'info':'heartbeat'})
				
			time.sleep(3)
	
	def run(self):
		while True:
			if self.connectStatus==False:
				self.startConnect()
				
			else:
				#jsonData={'test': 'test'}
				#try:
				#	jsonData=self.sendQueue.get(timeout=1)
				#except queue.Empty:
				#	continue
				jsonData=self.sendQueue.get()
				#print("[DATA]	SEND TO SERVER "+str(jsonData))
				self.sendData(jsonData)
				self.sendQueue.task_done()
				
command_thread = CommandThread(SERVER, COMMAND_PORT)
command_thread.start()

image_thread = ImageThread(SERVER, IMAGE_PORT)
image_thread.start()

while True:
	time.sleep(1)
