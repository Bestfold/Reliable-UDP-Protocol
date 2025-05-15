from socket import *
from drtpPacket import *
from .state import State

class LastAckState(State):
	'''
		Sending FIN ACK
	'''
	def enter(self):
		super().enter()

	def exit(self):
		pass

	def process(self):
		fin_ack_packet = create_packet(b'', 0, 0, 6, 0)
		self.parent.net_socket.sendto(fin_ack_packet, self.parent.counterpart_address)
		print("FIN-ACK packet sent")
		
		return self.parent.closedState