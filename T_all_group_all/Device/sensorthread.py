import serial  
import json
#import pymysql
import time
from queue import *
import threading
 
#def data_analysis(recieve,time):
	
#	tem_trans = str(recieve['Temperature'])
#	hum_trans = str(recieve['Humidity'])
#	time_trans = time
#	insert_db(time_trans,tem_trans,hum_trans)

	
#def insert_db(time,temperature,humidity):
#
#	conn = pymysql.connect("localhost","root","12345678","iot")
#	cursor = conn.cursor()
#	sql = "insert into TH(Time,Temperature,Humidity) values('%s','%s','%s')" % (time,temperature,humidity)
#	cursor.execute(sql)
#	conn.commit()
#	conn.close()

class ReadDataThread(threading.Thread):
	daemon = True
	DATA_TAG = 'default'
	COM_PORT = '/dev/cu.usbmodem1411'	
	BAUD_RATES = 9600
	ser = None
	
	stopThread = False
	resultQueue = None
	
	sendSocketThread = None
	
	def __init__(self,com,baud,queue,tag):
		threading.Thread.__init__(self)
		self.COM_PORT=com
		self.BAUD_RATES=baud
		self.resultQueue=queue
		self.DATA_TAG=tag
		try:
			self.ser = serial.Serial(self.COM_PORT, self.BAUD_RATES)
		except Exception as e:
			print(e)
			self.stopThread=True
	
	def stop(self):
		self.stopThread = True
	
	def set_send_socket_thread(self,socketthread):
		self.sendSocketThread=socketthread
	
	def run(self):
		while True:
			if self.stopThread==True:
				if self.ser != None:
					self.ser.close()
				break
				
			#do something
			while self.ser.in_waiting:	  

				recvData = self.ser.readline().decode('utf-8')
				current_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())) 

				while len(recvData):
					try:
						jsonData, decodeIndex = json.JSONDecoder().raw_decode(recvData)
						recvData=recvData[decodeIndex:]
					except ValueError:
						recvData=''
						break
					
					if self.sendSocketThread is not None:
						self.sendSocketThread.sendData({'data':jsonData,'time':current_time,'tag':self.DATA_TAG})
					else:
						self.resultQueue.put({'data':jsonData,'time':current_time,'tag':self.DATA_TAG})
			
			time.sleep(0.1)
		
		
	
class SensorThread():
	
	DATA_TAG = 'default'
	COM_PORT = 'COM5'	
	BAUD_RATES = 9600
	readDataThread = None
	resultQueue=Queue()
	#sendSocketThread = None
	
	def __init__(self,com,baud,tag):
		self.DATA_TAG=tag
		self.COM_PORT=com
		self.BAUD_RATES=baud
		self.readDataThread=ReadDataThread(self.COM_PORT,self.BAUD_RATES,self.resultQueue,tag)
		
	def start_thread(self):
		self.readDataThread.start()
	
	def stop_thread(self):
		self.readDataThread.stop()
		
	def set_send_socket_thread(self,socketthread):
		self.readDataThread.set_send_socket_thread(socketthread)
	
	def get_data(self):
		#resultQueue
		resultList=[]
		while True:
			try:
				resultData=self.resultQueue.get_nowait()
				#resultData['tag']=self.DATA_TAG
				resultList.append(resultData)
			except Empty:
				break
			else:
				#print(receiveData.decode('UTF-8', 'ignore'))
				self.resultQueue.task_done()
		
		return resultList
		
	
if __name__ == "__main__":

	#COM_PORT = '/dev/cu.usbmodem1411'	
	COM_PORT = 'COM4'
	BAUD_RATES = 9600	
	sensorThread=SensorThread(COM_PORT,BAUD_RATES)
	sensorThread.start_thread()
	while True:
		print(sensorThread.get_data())
		time.sleep(1)
	
	#ser = serial.Serial(COM_PORT, BAUD_RATES)

	#try:
	#	while True:
	#		while ser.in_waiting:		  
				# data_raw = ser.readline()  
				# data = data_raw.decode() 
				# # print('recv initial data：', data_raw)  # undecode
				# # print('recv data：', data)
				# print(data)
				# data_analysis(data)
	#			data_raw = ser.readline()
	#			current_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())) 
	#			if (len(data_raw)>10):				  # must be, because arduino can be none at first time
	#				data_json = json.loads(data_raw)
	#				data_analysis(data_json,current_time)
		
	#except KeyboardInterrupt:
	#	ser.close()	
	#	print('bye！')