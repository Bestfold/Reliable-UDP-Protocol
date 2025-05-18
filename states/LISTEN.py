from socket import *
from drtpPacket import *
from .state import State

SERVER_WINDOW = 15 # Size of max server receiver window. Set to 15

class ListenState(State):
	'''
		Listens for initial SYN

		State transfers:
		- SYN_RECVD when valid SYN received

		Handles:
		- valid SYN-packet (see process() )
	'''
	def enter(self):
		'''
			Called when this state becomes current_state of State Machine

			Sets "global" State Machine parameters now that receiver has been chosen.
			- effective_window_size to max receiver window size
			- Intantiates socket and binds to provided ip and port
		'''
		super().enter()

		# For readability:
		args = self.parent.args

		# Set the effective window size. Useful for server function
		self.parent.effective_window_size = SERVER_WINDOW

		# Resets counterpart_address when listening for new connection.
		self.parent.counterpart_address = None

		# Setting socket to be IPv4, UDP
		self.parent.net_socket = socket(AF_INET, SOCK_DGRAM)
		
		# Bind the socket to the server IP and port
		self.parent.net_socket.bind((args.ip, args.port))

	def exit(self):
		'''
			Called when this state is changed away from by State Machine

			Empty for maintanance
		'''

	def process(self):
		'''
			The "running" function call of the state

			Sends FIN_ACK packet before returning instance of CLOSED-state

			Handles:
			- flags
			- data size (should be 0)
		'''
		# Recieve potential SYN-packet from socket
		syn_packet, client_address = self.parent.net_socket.recvfrom(1024)

		# Unpack the header from the message
		data, _seq_num, _ack_num, flags, _window_size = dismantle_packet(syn_packet)
		
		# Chech that SYN packet is correct
		if flags == 8 and len(data) == 0:
			print("\nSYN packet is received")

			# Sets the counterpart_address only if it is correct SYN packet
			self.parent.counterpart_address = client_address
			return self.parent.synRecvdState
		else:
			pass
