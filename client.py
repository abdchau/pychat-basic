import socket
import json
import threading

class Client:
	def __init__(self, ip_address):
		self.host = ip_address
		self.port = 60000
		self.ID = None
		self.name = None

		self.incoming_messages = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
		self.incoming_messages.connect((self.host,self.port))

		self.outgoing_messages = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
		self.outgoing_messages.connect((self.host,self.port))

	def initialize_connection(self):
		self.name = input('What is your name? ')

		# requesting ID
		request = json.dumps({ 'request_type' : 0, 'id' : None, 'name' : self.name })
		self.outgoing_messages.send(request.encode('utf-8'))
		response = json.loads(self.outgoing_messages.recv(1024).decode('utf-8').rstrip("\x00"))
		if response['response_type'] == 0:
			self.ID = response['payload']
		print('You have been assigned the ID', self.ID)
		
		request = json.dumps({ 'request_type' : 0, 'id' : self.ID })
		self.incoming_messages.send(request.encode('utf-8'))

		print('You are now part of the conversation. Send a message!')


	def incoming(self):
		try:
			while True:
				response = json.loads(self.incoming_messages.recv(1024).decode("utf-8").rstrip("\x00"))
				if response['response_type'] == 1:
					message = response['payload']
					sender_name = response['sender_name']
					print(sender_name+':', message)
		except:
			pass

	def outgoing(self):
		while True:
			message = input()
			if message == 'exit':
				self.outgoing_messages.close()
				self.incoming_messages.close()
				break
			message = message.split(maxsplit=1)
			if int(message[0]) == self.ID:
				print('Error: Can\'t text yourself!')
				continue
			request = json.dumps({ 'request_type' : 1, 'id' : self.ID, 'recipient_id' : int(message[0]) ,'payload' : message[1] })
			self.outgoing_messages.send(request.encode('utf-8'))

	def run(self):
		self.initialize_connection()
		print('Type "exit" to exit the chat')
		print('Enter the message in the following format:\n<ID of intended recipient><space><message>')

		incoming_thread = threading.Thread(target=self.incoming)
		outgoing_thread = threading.Thread(target=self.outgoing)

		incoming_thread.start()
		outgoing_thread.start()

		incoming_thread.join()
		outgoing_thread.join()


if __name__=="__main__":
	ip_address = input("What ip do you wish to connect to?: ")
	
	try:
		client = Client(ip_address)
		client.run()
	except socket.error:
		print(socket.error.__str__())
		print("\n--------Error! Server is not available!--------")