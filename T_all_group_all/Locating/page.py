import flask
import threading
import time
import database

db_connect = database.DatabaseConnect()


FLASK_HOST = "0.0.0.0"
FLASK_PORT = 10007

app = flask.Flask(__name__,static_url_path='/static')
app.secret_key = 'super secret string'

fl_output_data="Hello"

@app.route('/')
def index():
	result_str = ""
	result_str += "<script language='JavaScript'>function myrefresh(){window.location.reload();}setTimeout('myrefresh()',1000);</script>"
	
	db_connect.start()
	loc_list = db_connect.get_all_loc()
	db_connect.close()
	#print(loc_list)
	for loc in loc_list:
		result_str += str(loc)
		result_str += '<br>\n'

	return result_str

class FlaskThread(threading.Thread):

	daemon = True

	def __init__(self, num):
		threading.Thread.__init__(self)
		self.num = num

	def set_data(self,data):
		fl_output_data = data

	def run(self):
		app.run(host=FLASK_HOST,port=FLASK_PORT)

if __name__ == '__main__':

	flaskThread = FlaskThread(3)
	flaskThread.start()
	flaskThread.set_data("quq")

	while True:
		time.sleep(1)
	
