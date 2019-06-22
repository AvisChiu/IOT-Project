import pymysql
import bcrypt

HOST='localhost'
USER='root'
PASSWORD='qwerty1234'
DATABASE='iot'

class DatabaseConnect():
	
	dbConnect=None
	
	def start(self):
		self.dbConnect = pymysql.connect(HOST,USER,PASSWORD,DATABASE)
	
	def createDevice(self,uuid):
		cursor = self.dbConnect.cursor()
		try:
			row = cursor.execute("INSERT INTO device (uuid) VALUES (%s)",(uuid))
			self.dbConnect.commit()
			if row!=0:
				return True
			else:
				return False
				
		except Exception as e:
			print(e)
			self.dbConnect.rollback()
			return False
		
		return False
		
	def getDevice(self,uuid):
		cursor = self.dbConnect.cursor()
		try:
			cursor.execute("SELECT * FROM device WHERE uuid = %s ;", uuid)
			device = cursor.fetchone()
			cursor.close()

			if len(device) > 0 :
				devDict={}
				devDict['id']=device[0]
				devDict['level']=device[2]
				return devDict
		except Exception as e:
			print(e)
		
		return
		
	def getAllDevice(self):
		cursor = self.dbConnect.cursor()
		try:
			cursor.execute("SELECT * FROM device ;")
			deviceRows = cursor.fetchall()
			cursor.close()
			
			devUUIDDict={}
			#print("OUCH")
			for row in deviceRows:
				devDict={}
				devDict['id']=row[0]
				devDict['level']=row[2]
				
				devUUIDDict[row[1]]=devDict
			
			return devUUIDDict
			
		except Exception as e:
			print(e)
		
		return
	
	def createUser(self,email,pwd,name):
		hash_pwd = bcrypt.hashpw(pwd.encode('utf-8'),bcrypt.gensalt())
		cursor = self.dbConnect.cursor()
		try:
			row = cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",(name,email,hash_pwd))
			self.dbConnect.commit()
			if row!=0:
				return True
			else:
				return False
			
		except Exception as e:
			print(e)
			self.dbConnect.rollback()
			return False
		
		return False
	
	def getUser(self,email):
		cursor = self.dbConnect.cursor()
		try:
			cursor.execute("SELECT * FROM users WHERE email = %s ;", email)
			user = cursor.fetchone()
			cursor.close()
			print(user)
			if len(user) > 0 :
				return user
		except Exception as e:
			print(e)
		
		return
	
	def loginUser(self,email,pwd):
		pwd = pwd.encode('utf-8')
		cursor = self.dbConnect.cursor()
		try:
			cursor.execute("SELECT * FROM users WHERE email = %s ;", email)
			user = cursor.fetchone()
			cursor.close()
			print(user)
			if len(user) > 0 :
				if bcrypt.hashpw(pwd, user[2].encode('utf-8')):
					return user
			
		except Exception as e:
			print(e)
		
		return None
	
	def insertData(self,uuid,data):
		
		if data['tag']=='env':
			cursor = self.dbConnect.cursor()
			sql = "insert into th(Time,UUID,Temperature,Humidity) values('%s','%s','%s','%s')" % (data['time'],uuid,data['data']['Temperature'],data['data']['Humidity'])
			try:
				cursor.execute(sql)
				self.dbConnect.commit()
			except:
				self.dbConnect.rollback()
				
		else:
			pass
			
	def getData(self,tag,config):
		data=[]
		if tag=='env_live':
			if config:
				length = config.get('len')
				start_time = config.get('start')
			else:
				length = 20
				start_time = '1970-01-01 00:00:01'
				
			sql = "(select * from th where time > %s order by time desc limit %s) order by time asc;"
			cursor = self.dbConnect.cursor()
			try:
				cursor.execute(sql,(start_time,length))
				results = cursor.fetchall()
				for row in results:
					rowData={}
					rowData['time']=str(row[0])
					rowData['uuid']=row[1]
					rowData['temp']=row[2]
					rowData['humi']=row[3]
					data.append(rowData)
					
				return {'envdata':data}
			except:
				pass
		
		if tag=='env':
			#parse config dict
			if config:
				start_time = config.get('start')
				end_time = config.get('end')
				sql = "select * from th where time between %s and %s order by time asc;"
			else:
				#not configured, show all data
				sql = "select * from th order by time asc;"
			#get data
			cursor = self.dbConnect.cursor()
			#sql = "select * from th order by time asc;"
			try:
				if config:
					cursor.execute(sql,(start_time,end_time))
				else:
					cursor.execute(sql)
				results = cursor.fetchall()
				for row in results:
					rowData={}
					rowData['time']=str(row[0])
					rowData['uuid']=row[1]
					rowData['temp']=row[2]
					rowData['humi']=row[3]
					data.append(rowData)
					
				return {'envdata':data}
			except:
				pass
		else:
			pass
			
		return {}
		
	def close(self):
		self.dbConnect.close()