import socket
import time
import threading
import json
import uuid


def get_uuid():

    get_uuid = (uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org'))
    # get_uuid = (uuid.uuid4())
    return str(get_uuid)


def get_mac_address():

    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)])


def get_host_ip():      # use udp to catch self ip

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def sendSelfData():

	sendlist = []
	ip = get_host_ip()        # client
	sendlist.append(ip)
	mac = get_mac_address()
	sendlist.append(mac)
	uuid = get_uuid()
	sendlist.append(uuid)
	return(sendlist)


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

		json_string = json.dumps(sendSelfData())
		sk.sendall(json_string.encode("utf8"))
		# sk.sendall((ip).encode("utf8"))
		data = sk.recv(1024)
		print(data.decode('UTF-8', 'ignore'))
		time.sleep(1)


if __name__ == "__main__":

	ip="140.112.29.209"
	port=10023
	conn = threading.Thread(target = connect)
	conn.start()


	


