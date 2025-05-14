from socket import *
from drtpPacket import *
from .state import State

class ListenState(State):
	'''
		Serverside
		Listening for incomming requests to communicate (SYN packets)
	'''
	def enter(self):
		super().enter()

		# For readability:
		args = self.parent.args

		# Set the effective window size. Useful for client and server function
		self.parent.effective_window_size = args.window

		# Resets counterpart_address when listening for new connection.
		self.parent.counterpart_address = None

		# Setting socket to be IPv4, UDP
		self.parent.net_socket = socket(AF_INET, SOCK_DGRAM)
		
		# Bind the socket to the server IP and port
		self.parent.net_socket.bind((args.ip, args.port))
		print(f"Ready to serve on {args.ip}:{args.port}\n")

	def exit(self):
		pass

	def process(self):
		# Recieve potential SYN-packet from socket
		syn_packet, client_address = self.parent.net_socket.recvfrom(1024)

		# Unpack the header from the message
		data, seq_num, ack_num, flags, window_size = dismantle_packet(syn_packet)
		
		# Chech that SYN packet is correct
		if flags == 8 and len(data) == 0:
			print("SYN packet is received")

			# Sets the counterpart_address only if it is correct SYN packet
			self.parent.counterpart_address = client_address
			return self.parent.synRecvdState
		else:
			pass