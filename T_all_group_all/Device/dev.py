#!/usr/bin/env python3

import requests
import uuid
import platform
import json
import pickle
import psutil #pip install psutil
import time

import clientsocketthread as cst
import sensorthread as sensort

#SERVER='127.0.0.1'
SERVER='iot.fakefact.me'
PORT=10000
SOCKETPORT=10001
#UUID=uuid.uuid4()
UUID=None

clientSocketThread=None

def initData():
	global UUID
	try:
		f = open('store.pckl', 'rb')
		UUID = pickle.load(f)
		NODE = pickle.load(f)
		f.close()
	except (EOFError,OSError) as e:
		print("NO UUID")
		newUUID()
		return;
	
	if NODE != uuid.getnode():
		print("DEVICE CHANGED")
		newUUID()
	
	
def newUUID():
	global UUID
	UUID=uuid.uuid4()
	NODE=uuid.getnode()
	try:
		f = open('store.pckl', 'wb')
		pickle.dump(UUID, f)
		pickle.dump(NODE, f)
		f.close()
	except (OSError) as e:
		print("SAVE NEW UUID ERROR")
		

def checkInternet():
	serverAddr='https://'+SERVER+':'+str(PORT)+'/'
	#serverAddr='http://'+SERVER+':'+str(PORT)+'/'
	timeout=5
	try:
		_=requests.get(serverAddr,timeout=timeout)
		return True
	except requests.ConnectionError:
		#print ("connection err")
		pass
	return False

def sayHello():
	print("SEND HELLO DATA")
	global UUID
	serverAddr='http://'+SERVER+':'+str(PORT)+'/dev/'
	
	helloData = {}
	
	helloData['uuid'] = str(UUID)
	helloData['machine'] = platform.machine()
	helloData['platform'] = platform.platform()
	helloData['python'] = platform.python_version()
	helloData['memory'] = dict(psutil.virtual_memory()._asdict())
	#print(psutil.cpu_percent())
	#print(psutil.virtual_memory())
	#print(dict(psutil.virtual_memory()._asdict()))
	print(UUID)
	#print(platform.machine())
	#print(platform.version())
	#print(platform.platform())
	#print(platform.uname())
	#print(platform.processor())
	#print(platform.python_version())
	helloReq = requests.post(serverAddr, json=helloData)
	print(helloReq.text)
	
def main():
	#print(uuid.getnode())
	initData()
	#print('OK')
	while checkInternet()==False:
		print("TRY CONNECTION FAIL")
	#sayHello()
	
	clientSocketThread=cst.ClientSocketThread(SERVER,SOCKETPORT,str(UUID))
	clientSocketThread.start_thread()
	
	# generate hello data
	helloData = {}
	
	#helloData['uuid'] = str(UUID)
	helloData['machine'] = platform.machine()
	helloData['platform'] = platform.platform()
	helloData['python'] = platform.python_version()
	#helloData['memory'] = dict(psutil.virtual_memory()._asdict())
	
	clientSocketThread.sendData({"data":helloData,"tag":"hello"})
	
	#COM_PORT = 'COM5'
	#BAUD_RATES = 9600
	#sensorThread=sensort.SensorThread(COM_PORT,BAUD_RATES,'env')
	#sensorThread.start_thread()
	
	#sensorThread.set_send_socket_thread(clientSocketThread)
	
	sensorThreadList=[]
	currentConfig=[]

	while True:
		
		#recvDataList=clientSocketThread.recvData()
		#if len(recvDataList)!=0:
		#	print("RECEIVE DATA FROM SERVER"+str(recvDataList))
		
		#for data in recvDataList:
		#	if data.get('conf'):
		#		print("[CONF] Config "+ str(data))

		#time.sleep(1)
		recvData=clientSocketThread.recvData()
		print("[DATA]	RECV FROM SERVER "+str(recvData))
		
		# receive config
		recvConf=recvData.get('conf')
		if recvConf is not None:
			print("[CONF]	RECV CONFIG "+ str(recvData))
			# handle config
			if recvConf=="":
				print("[CONF]	RESET CONFIG")
				for sT in sensorThreadList:
					sT.stop_thread()
				
				sensorThreadList=[]
				currentConfig=[]
				
				
			if isinstance(recvConf,(list,)):
				currentConfig+=recvConf
				for conf in recvConf:
					if conf.get('type')=='serial':
						com=conf.get('com')
						baud=conf.get('baud')
						tag=conf.get('tag')
						sensorThread=sensort.SensorThread(com,baud,tag)
						sensorThread.start_thread()
						sensorThread.set_send_socket_thread(clientSocketThread)
						sensorThreadList.append(sensorThread)
		
	
	sensorThread.stop_thread()
	clientSocketThread.stop_thread()
	

if __name__ == '__main__':
	main()