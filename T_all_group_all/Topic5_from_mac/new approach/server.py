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

normal_speed = 0.30
line_left_max = 0.3
line_right_max = 0.7

turn_left_max = 0.0
turn_right_max = 1.0
turn_speed = 0.47
turn_time = 2

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
device_socket_dict={}
device_state_dict={}
video_client_dict={}

def create_device_state(ip):
	device_state_dict[ip] = {}
	device_state_dict[ip]['run'] = False
	device_state_dict[ip]['turn'] = False
	device_state_dict[ip]['turn_count'] = 0
	# device_state_dict[ip]['turn_action'] = [2,2,1,2,1,1,0,0,0]
	# device_state_dict[ip]['turn_action'] = [2,2,1,1,2,2,1,1,0,0,0]
	# device_state_dict[ip]['turn_action'] = [2,2,1,1,2,0,0]
	device_state_dict[ip]['turn_action'] = [0,1,2,1,0,0,0]
	device_state_dict[ip]['angle_mod'] = -0.05
	device_state_dict[ip]['channel'] = 2
	

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

		clientDict[self.client_address] = self.request
		device_socket_dict[self.ip] = self.request
		create_device_state(self.ip)
		
		
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
		del(device_socket_dict[self.ip])
		del(device_state_dict[self.ip])
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
				cv_thread.put_image((self.ip, image, device_state_dict[self.ip]['channel']))
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

def send_command(ip,command):
	socket = device_socket_dict.get(ip)
	if socket is not None:
		socket.sendall((json.dumps(command)).encode('utf-8'))

class CommandCVThread(cv.CVThread):
	def send_result(self,ip,result):
		angle = result.get('A')
		print("A "+str(angle))
		if device_state_dict[ip]['run'] == True:

			if result.get('T') is not None:
				if device_state_dict[ip]['turn'] is False:
					device_state_dict[ip]['turn'] = True
					print('T1')
					try:
						count = device_state_dict[ip]['turn_count']
						action = device_state_dict[ip]['turn_action'][count]
					except Exception as e:
						print(e)
						action = 0
				
					# handle turn action
						
					if action == 0:
						# go straight
						time.sleep(3)
						device_state_dict[ip]['turn'] = False
						device_state_dict[ip]['turn_count'] += 1
						return
						
					elif action == 1:
						# turn right
						send_command(ip,{'A': turn_right_max, 'S': turn_speed})
					
					else:
						# turn left
						send_command(ip,{'A': turn_left_max, 'S': turn_speed})
						
					time.sleep(2)
					return
				
			if device_state_dict[ip]['turn'] is True:
					# turning
					# detect end
					
				if angle < 0.65 and angle > 0.35:
					send_command(ip,{'A': 0.5, 'S': normal_speed})
						
					
					print('T2')
					device_state_dict[ip]['turn'] = False
					device_state_dict[ip]['turn_count'] += 1
				
		
		else:
			send_command(ip,{'S': 0})
		
		# turning
		if device_state_dict[ip]['turn'] == True:
			return
			
		# follow line
		angle = result.get('A')
		if angle is not None:
			if angle > line_right_max:
				angle = line_right_max
			if angle < line_left_max:
				angle = line_left_max
			send_command(ip,{'A': angle})
			
cv_thread = CommandCVThread()
cv_thread.start()
print("CV START")

run_state = False

while True:
	input("")
	run_state = not run_state
	print(run_state)
	if run_state:
		command = {'S': normal_speed}
	else:
		command = {'S': 0.0}
		
	for ip, dev_state in device_state_dict.items():
		device_state_dict[ip]['run'] = run_state
		print(device_state_dict[ip]['run'])
		send_command(ip,command)
	#for index, socket in deviceDict.items():
	#	socket.sendall((json.dumps(command)).encode('utf-8'))