import socket
import time
import threading

def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))
		
def connect():

	sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sk.connect((ip,port))

	while True:
		sk.sendall((ip).encode("utf8"))
		data = sk.recv(1024)
		print(data.decode('UTF-8', 'ignore'))
		time.sleep(1)
		

		
if __name__ == "__main__":
	ip="127.0.0.1"
	port=10023
	
	conn = threading.Thread(target = connect)
	conn.start()
