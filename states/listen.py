from socket import *
from .state import State

class ListenState(State):
	def enter(self):
		super().enter()

		# For readability:
		net_socket = self.parent.net_socket
		print(net_socket)
		args = self.parent.args
		
		# Bind the socket to the server IP and port
		net_socket.bind((args.ip, args.port))
		print(f"Ready to serve on {args.ip}:{args.port}")

	def exit(self):
		pass

	def process(self):
		net_socket = self.parent.net_socket

		# Recieve potential SYN-packet from socket
		syn_packet, client_address = net_socket.recvfrom(1024)
		#TODO check for SYN


		return self.parent.closedState