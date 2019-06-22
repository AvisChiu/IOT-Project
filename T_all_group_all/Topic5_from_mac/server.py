import threading
import socketserver
import cv2
import time
import numpy as np
import cv
import json
import queue
import socket

HOST = '0.0.0.0'
VIDEO_PORT = 10037
COMMAND_PORT = 10040

cv_thread = cv.CVThread()
cv_thread.start()
print("CV START")

#class SensorDataHandler(socketserver.BaseRequestHandler):
#	data = " "
#	def handle(self):
#		global sensor_data
#		while self.data:
#			self.data = self.request.recv(1024)
#			sensor_data = round(float(self.data), 1)
#			print "{} sent:".format(self.client_address[0])
#			print(sensor_data)

clientDict={} # client_address:client_socket
video_client_dict={}

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

	ip = ""
	port = 0
	timeOut = 6
	receiveQueue = queue.Queue()
	
	def setup(self):
		self.ip = self.client_address[0].strip()
		self.port = self.client_address[1]
		self.request.settimeout(self.timeOut)
		print("[INFO]	"+self.ip+":"+str(self.port)+" COMMAND CONNECTED")

		clientDict[self.client_address]=self.request
		
	
	def handle(self):
		recvData=''
		while True:
			try:
				recvTemp=self.request.recv(1024)
				if recvTemp == b'':
					break
				recvData+=recvTemp.decode('utf-8')
				
			except socket.timeout:
				print("[INFO]	"+self.ip+":"+str(self.port)+"接收超时！即将断开连接！")
				break
				
			except Exception as e:
				print("[ERR]	"+str(e))
				break


			while len(recvData):
				
				try:
					jsonData, decodeIndex = json.JSONDecoder().raw_decode(recvData)
					recvData=recvData[decodeIndex:]
				except ValueError:
					recvData=''
					break
				
				
				#print(jsonData)
				#receiveDict = {'uuid': self.deviceUUID, 'data': jsonData}
				#self.receiveQueue.put({'ip':self.ip, 'data':jsonData})
				self.receiveQueue.put((self.ip, jsonData))
				
	def finish(self):

		del(clientDict[self.client_address])	
		print("[INFO]	"+self.ip+":"+str(self.port)+"断开连接！")


class VideoStreamHandler(socketserver.StreamRequestHandler):

	ip = ""
	port = 0
	timeOut = 6

	def setup(self):
		super().setup()
		self.ip = self.client_address[0].strip()
		self.port = self.client_address[1]
		self.request.settimeout(self.timeOut)
		print("[INFO]	"+self.ip+":"+str(self.port)+" VIDEO CONNECTED")

		video_client_dict[self.client_address]=self.request

	def handle(self):

		stream_bytes = b' '

		# stream video frames one by one
		while True:
			stream_bytes += self.rfile.read(1024)
			first = stream_bytes.find(b'\xff\xd8')
			last = stream_bytes.find(b'\xff\xd9')
			if first != -1 and last != -1:
				jpg = stream_bytes[first:last + 2]
				stream_bytes = stream_bytes[last + 2:]
				gray = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
				image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
				cv_thread.put_image((self.ip, image))
				#print("OK")
			
			if len(stream_bytes) == 0:
				break
				
	def finish(self):
		super().finish()
		del(video_client_dict[self.client_address])	
		print("[INFO]	"+self.ip+":"+str(self.port)+" VIDEO DISCONNECTED")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass




video_server = ThreadedTCPServer((HOST, VIDEO_PORT), VideoStreamHandler)
video_server_thread = threading.Thread(target=video_server.serve_forever)
video_server_thread.daemon = True
video_server_thread.start()  
print("VIDEO SERVER START")

command_server = ThreadedTCPServer((HOST, COMMAND_PORT), ThreadedTCPRequestHandler)
command_server_thread = threading.Thread(target=command_server.serve_forever)
command_server_thread.daemon = True
command_server_thread.start()  
print("COMMAND SERVER START")


while True:
	time.sleep(1)				 