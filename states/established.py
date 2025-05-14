from socket import *
from drtpPacket import *
from .state import State

class EstablishedState(State):
	def enter(self):
		super().enter()
		# Sending ACK packet to server
		ack_packet = create_packet(b'', seq_num, ack_num, 4, arg_window)
		client_socket.sendto(ack_packet, server_address)
		print(f"Sent ACK packet to server {server_address}")

		return server_window

	def exit(self):
		pass

	def process(self):
		pass