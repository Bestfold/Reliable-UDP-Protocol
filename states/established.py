from socket import *
from drtpPacket import *
from .state import State

class EstablishedState(State):
	def enter(self):
		super().enter()

		# Send final ACK of handshake if client
		if self.parent.args.client:
			self.send_ack()


	def exit(self):
		pass

	def process(self):
		pass




	def send_ack(self):
			# Sending ACK packet to server
			ack_packet = create_packet(b'', 0, 0, 4, self.parent.args.window)

			self.parent.net_socket.sendto(ack_packet, self.parent.counterpart_address)
			print(f"Sent ACK packet to server {self.parent.counterpart_address}")