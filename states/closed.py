import sys
from socket import *
from drtpPacket import *
from .state import State

class ClosedState(State):
	def __init__(self, name, parent):
		super().__init__(name, parent)
		self.first_run = True

	def enter(self):
		super().enter()

		if not self.first_run:
			if self.parent.net_socket:
				self.parent.net_socket.close()
			sys.exit(1)
		
		# Set up socket for IPv4 and UDP
		self.parent.net_socket = socket(AF_INET, SOCK_DGRAM)
		print(self.parent.net_socket)


	def exit(self):
		self.first_run = False


	def process(self):
		# For readability
		net_socket = self.parent.net_socket
		args = self.parent.args

		if args.server:
			return self.parent.listenState
		
		elif args.client:
			#TODO Send SYN packet
			# Creating SYN packet
			syn_packet = create_packet(b'', 0, 0, 8, args.window)

			# Sending SYN packet
			net_socket.send(syn_packet, (args.ip, args.port))

			return self.parent.synSentState