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
		# Calculated Mbps throughput with 2 desimals
		print(f"\nThe throughput is {self.parent.throughput:.2f} Mbps")

		# Write self.parent.file data to file tree
		self.save_file()

	def process(self):
		# Send FIN_ACK packet
		fin_ack_packet = create_packet(b'', 0, 0, 6, 0)
		self.parent.net_socket.sendto(fin_ack_packet, self.parent.counterpart_address)
		print("FIN-ACK packet sent")
		
		return self.parent.closedState
	

	def save_file(self):
		'''
			Writes data on self.parent.file
		'''
		try:
			file_data = self.parent.file
			with open('recieved_data.jpg', 'wb') as new_file:
				new_file.write(file_data)

		except Exception as e:
			print(f"Error reading file: {e}")