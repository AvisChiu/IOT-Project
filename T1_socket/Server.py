
#!/usr/bin/python3
# coding:utf-8
import socket
import threading
import socketserver
import time
 
client_addr = []
client_socket = []
 
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
 
    ip = ""
    port = 0
    timeOut = 6     # 设置超时时间变量
 
    def setup(self):
        
        self.ip = self.client_address[0].strip()     # 获取客户端的ip
        self.port = self.client_address[1]           # 获取客户端的port
        self.request.settimeout(self.timeOut)        # 对socket设置超时时间
        print(self.ip+":"+str(self.port)+"连接到服务器！")
        client_addr.append(self.client_address) # 保存到队列中
        client_socket.append(self.request)      # 保存套接字socket
 
    def handle(self):
        while True: # while循环
            try:
                data = str(self.request.recv(1024), 'ascii')

                print(data)             ######################################################## the data from client #########################################

            except socket.timeout:  # 如果接收超时会抛出socket.timeout异常
                print(self.ip+":"+str(self.port)+"接收超时！即将断开连接！")
                break       # 记得跳出while循环
 
            if data:    # 判断是否接收到数据
                cur_thread = threading.current_thread()
                response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
                self.request.sendall(response)
 
    def finish(self):
        print(self.ip+":"+str(self.port)+"断开连接！")
        client_addr.remove(self.client_address)
        client_socket.remove(self.request)

 
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
 

 
if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "140.112.29.209", 10023
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)
    message = bytes("clientTest\n", "ascii")

    while True:
        time.sleep(2)
        print("\nclient_addr:"+str(client_addr))
        if client_addr:
            for c_socket in client_socket:
                c_socket.sendall(message)	
			#client_socket[0].sendall(message)
    #
    server.shutdown()
    server.server_close()
