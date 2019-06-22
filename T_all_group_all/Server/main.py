#!/usr/bin/env python3

#from flask import Flask
#from flask import request
#from flask import render_template
import datetime
import flask_login
import flask
import socketthread as st
import time
import database as db
import json
import bcrypt

HOST = '0.0.0.0'
PORT = 10000
SOCKETPORT = 10001

app = flask.Flask(__name__,static_url_path='/static')
app.secret_key = 'super secret string'  # Change this!


login_manager = flask_login.LoginManager()
login_manager.init_app(app)

#users = {'foo@bar.tld': {'password': 'secret','level': 0}}
users_info = dict()
#{'test@test.test': (9, 'test@test.test', '$2b$12$.uFWZcrtIR/9b4.wbm1IvOwwVqoFQAXeFm9oVj219MwXHmIGEO9De', 'test', 5)}


devices = {'3f0508cf-2a0b-4827-a5c6-52b4bcc6ba12': {'level': 1}}

socketThread=st.SocketThread(SOCKETPORT)


class User(flask_login.UserMixin):
	pass


@login_manager.user_loader
def user_loader(email):
	if email not in users_info:
		return

	user = User()
	user.id = email
	user.name = users_info[email][3]
	user.level = users_info[email][4]
	return user


@login_manager.request_loader
def request_loader(request):
	email = request.form.get('email')
	if email not in users_info:
		return

	user = User()
	user.id = email
	user.name = users_info[email][3]
	user.level = users_info[email][4]

	# DO NOT ever store passwords in plaintext and always compare password
	# hashes using constant-time comparison!
	
	user.is_authenticated = bcrypt.hashpw(request.form['password'],users_info[email][2])
	return user
	
	
@app.route('/register', methods=["GET","POST"])
def register():
	if flask.request.method == 'GET':
		return flask.render_template("register.html")
		
	name = flask.request.form['name']
	email = flask.request.form['email']
	password = flask.request.form['password']

	
	
	databaseConnect = db.DatabaseConnect()
	databaseConnect.start()
	result = databaseConnect.createUser(email,password,name)
	databaseConnect.close()
	
	if result:
		#register success, redirect to login
		return flask.redirect(flask.url_for('login'))
	
	#if not users.get(email):
	#	users[email]={'password':password, 'level':0}
	#	print(users)
	
	#register fail, redirect to register
	return flask.redirect(flask.url_for('register'))
	
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return flask.render_template("login.html")
		#return '''
		#	   <form action='login' method='POST'>
		#		<input type='text' name='email' id='email' placeholder='email'/>
		#		<input type='password' name='password' id='password' placeholder='password'/>
		#		<input type='submit' name='submit'/>
		#	   </form>
		#	   '''

	email = flask.request.form['email']
	password = flask.request.form['password']
	#if email not in users:
	#	return flask.abort(403)
	
	#if flask.request.form['password'] == users[email]['password']:
	#	user = User()
	#	user.id = email
	#	flask_login.login_user(user)
	#	return flask.redirect(flask.url_for('index'))
	databaseConnect = db.DatabaseConnect()
	databaseConnect.start()
	result = databaseConnect.loginUser(email,password)
	databaseConnect.close()
	
	if result != None:
		#load user to info dict
		users_info[email]=result
		print(users_info)
		
		user = User()
		user.id = email
		user.name = users_info[email][3]
		user.level = users_info[email][4]
		flask_login.login_user(user)
		
		return flask.redirect(flask.url_for('index'))
	
	return flask.abort(403)


@app.route('/protected')
@flask_login.login_required
def protected():
	return 'Logged in as: ' + flask_login.current_user.id
	
	
@app.route('/logout')
def logout():
	flask_login.logout_user()
	return flask.redirect(flask.url_for('index'))
	
	
@login_manager.unauthorized_handler
def unauthorized_handler():
	#return 'Unauthorized'
	return flask.abort(403)
	
@app.route('/')
def index():
	if flask_login.current_user.is_anonymous:
		return flask.render_template("index.html")
	

	user_level=flask_login.current_user.level
	deviceDict=socketThread.get_device_by_level(user_level)
	
	
	
	return flask.render_template("index_u.html",user_id=flask_login.current_user.name,devices = deviceDict)

@app.route('/config/',methods=['GET','POST'])
def multi_config():
	user_level=flask_login.current_user.level	
	deviceDict=socketThread.get_device_by_level(user_level)
	
	if flask.request.method == 'POST':
		configDevice=flask.request.form.getlist('device')
		print(configDevice)
		configJSON = flask.request.form.get('config')
		configAction = flask.request.form.get('action')
		if configAction == "Reset":
			try:
				for uuid in configDevice:
					socketThread.send_config_to_device(uuid,"")
				
				info={"status": True, "text": "The config has been reseted."}
				return flask.render_template("config.html",info = info,devices = deviceDict)
			except Exception as e:
				info={"status": False, "text": "Error: "+str(e)}
				print(e)
				return flask.render_template("config.html",info = info,devices = deviceDict)

	
		try:
			configObject = json.loads(configJSON)
		except Exception as e:
			info={"status": False, "text": "Error: "+str(e)}
			print(e)
			return flask.render_template("config.html",info = info,devices = deviceDict)
		
		#check configObject
	
		#apply config
		for uuid in configDevice:
			socketThread.send_config_to_device(uuid,configObject)
	
		info={"status": True, "text": "The config has been delivered."}
		return flask.render_template("config.html",info = info,devices = deviceDict)
	
	return flask.render_template("config.html",devices = deviceDict)



@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/data/env')
@flask_login.login_required
def show_env_data():
	return flask.render_template("env.html")


@app.route('/data/env_live')
@flask_login.login_required
def show_env_live_data():
	return flask.render_template("env_live.html")
	
@app.route('/js/<path:path>')
def send_js(path):
    return flask.send_from_directory('js', path)


@app.route('/data/env.json')
@flask_login.login_required
def get_env_json():

	start=flask.request.args.get('s', default = '1970-01-01 00:00:01', type = str)
	end=flask.request.args.get('e', default = str(datetime.datetime.now()), type = str)

	databaseConnect=db.DatabaseConnect()
	databaseConnect.start()

	data=databaseConnect.getData('env', {'start':start, 'end':end})

	databaseConnect.close()
	return json.dumps(data)

@app.route('/data/env_live.json')
@flask_login.login_required
def get_env_live_json():
	start=flask.request.args.get('s', default = '1970-01-01 00:00:01', type = str)
	length=flask.request.args.get('l', default = 50, type = int)
	
	databaseConnect=db.DatabaseConnect()
	databaseConnect.start()

	data=databaseConnect.getData('env_live', {'start':start,'len':length})

	databaseConnect.close()
	return json.dumps(data)



	
#@app.route('/dev/',methods=['GET','POST'])
@app.route('/dev/<string:uuid>/',methods=['GET'])
def device_page(uuid):
	deviceDict=socketThread.get_device()
	
	deviceObj = deviceDict.get(uuid)
	
	if deviceObj is None:
		return flask.abort(404)
	
	return flask.render_template("dev_u.html",uuid = uuid,device = deviceObj)

@app.route('/dev/<string:uuid>/',methods=['POST'])
def device_config(uuid):
	deviceDict=socketThread.get_device()
	
	deviceObj = deviceDict.get(uuid)
	
	if deviceObj is None:
		return flask.abort(404)
		
	configJSON = flask.request.form.get('config')
	configAction = flask.request.form.get('action')
	if configAction == "Reset":
		try:
			socketThread.send_config_to_device(uuid,"")
			info={"status": True, "text": "The config has been reseted."}
			return flask.render_template("dev_u.html",info = info,uuid = uuid,device = deviceObj)
		except Exception as e:
			info={"status": False, "text": "Error: "+str(e)}
			print(e)
			return flask.render_template("dev_u.html",info = info,uuid = uuid,device = deviceObj)

	
	try:
		configObject = json.loads(configJSON)
	except Exception as e:
		info={"status": False, "text": "Error: "+str(e)}
		print(e)
		return flask.render_template("dev_u.html",info = info,uuid = uuid,device = deviceObj)
		
	#check configObject
	
	#apply config
	socketThread.send_config_to_device(uuid,configObject)
	
	info={"status": True, "text": "The config has been delivered."}
	return flask.render_template("dev_u.html",info = info,uuid = uuid,device = deviceObj)


def main():
	#print('OK')
	
	#create socket thread
	#st.start_thread()
	
	socketThread.start_thread()
	
	
	
	#run flask
	app.run(host=HOST,port=PORT,threaded=True,ssl_context=('fullchain.pem', 'privkey.pem'))
	#app.run(host=HOST,port=PORT,threaded=True)
	#while True:
	#	print(socketThread.get_device())
	#	time.sleep(1)
	
	#close socket server while flask close
	socketThread.stop_thread()
	
	

if __name__ == '__main__':
	main()