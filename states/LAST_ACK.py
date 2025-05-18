from socket import *
from drtpPacket import *
from .state import State

class LastAckState(State):
	'''
		Sending FIN_ACK before signaling change of state to CLOSED
		
		Saving saved file-data on exiting

		State transfers:
		- CLOSED immideatly after sending FIN_ACK-packet
	'''
	def enter(self):
		'''
			Called when this state becomes current_state of State Machine

			Empty for maintanance
		'''
		super().enter()

	def exit(self):
		'''
			Called when this state is changed away from by State Machine

			Prints throughput calculated in ESTABLISHED.

			Writes received file-data to storage 
		'''
		# Calculated Mbps throughput with 2 desimals
		print(f"\nThe throughput is {self.parent.throughput:.2f} Mbps")

		# Write self.parent.file data to file tree
		self.save_file()


	def process(self):
		'''
			The "running" function call of the state

			Sends FIN_ACK packet before returning instance of CLOSED-state
		'''
		# Send FIN_ACK packet
		fin_ack_packet = create_packet(b'', 0, 0, 6, 0)
		self.parent.net_socket.sendto(fin_ack_packet, self.parent.counterpart_address)
		print("FIN-ACK packet sent")
		
		return self.parent.closedState
	

	def save_file(self):
		'''
			Writes data from self.parent.file to current directory

			Handles:
			- Exceptions when opening and writing data.
		'''
		try:
			file_data = self.parent.file
			with open('recieved_data.jpg', 'wb') as new_file:
				new_file.write(file_data)

		except Exception as e:
			print(f"Error reading file: {e}")