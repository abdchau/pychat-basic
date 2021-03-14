import json
import socket
import threading
from _thread import start_new_thread

# request_types = { 0 : id management, 1 : message, 2 : terminate connection }
# request = { id : , payload : , request_type : }

# response_types = { 0 : giving new id, 1 : message}
# response = { response_type : , sender_name : , payload : }

class Server:
	def __init__(self):
		self.host = 'localhost'
		self.port = 60000
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = {}
		self.new_client_lock = threading.Lock()
		self.broadcast_lock = threading.Lock()

		try:
			self.sock.bind((self.host,self.port))
		except socket.error as e:
			print(str(e))

		self.sock.listen()
		print("Server is ready! Waiting for connection...")

	def handle_incoming_messages(self, socket):
		while True:
			try:
				request = json.loads(socket.recv(1024).decode("utf-8").rstrip("\x00"))
				if request['request_type'] == 1:
					message = request['payload']
					print(request)
					sender_name = self.clients[request['id']]['name']
					self.broadcast_lock.acquire()
					self.broadcast(sender_name, message, request['id'], request['recipient_id'])
					self.broadcast_lock.release()
			except:
				pass

	def broadcast(self, name, message, id, recipient_id):
		response = json.dumps({ 'response_type' : 1, 'sender_name' : name, 'payload' : message })
		self.clients[recipient_id]['outgoing_socket'].send(response.encode('utf-8'))

	def handle_new_conn(self, socket):
		r = socket.recv(1024).decode("utf-8").rstrip("\x00")
		request = json.loads(r)

		if request['request_type'] == 0:

			if request['id'] == None:
				self.new_client_lock.acquire()
				new_ID = len(self.clients)
				self.clients[new_ID] = { 'incoming_socket' : socket, 'name' : request['name'] }
				self.new_client_lock.release()
				response = json.dumps({ 'response_type' : 0, 'payload' : new_ID })
				socket.send(response.encode('utf-8'))
				print(self.clients)
				self.handle_incoming_messages(socket)

			else:
				self.clients[request['id']]['outgoing_socket'] = socket

	def run(self):
		while True:
			socket, addr = self.sock.accept()
			print("New connection accepted: ", socket, addr)
			start_new_thread(self.handle_new_conn, (socket,)) # Create new thread with process and connection object

if __name__ == '__main__':
	server = Server()
	server.run()