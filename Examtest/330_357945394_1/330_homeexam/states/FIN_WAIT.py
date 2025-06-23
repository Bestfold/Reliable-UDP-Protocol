from socket import *
from drtpPacket import *
from .state import State

TIMEOUT = 0.4 # 400ms
MAX_ATTEMPTS = 5

class FinWaitState(State):
	'''
		Connection Teardown from client side.

		Send FIN packet 
		and await FIN-ACK from server before shutting down.

		Will wait MAX_ATTEMPTS amount of times before shutting down

		State transfers:
		- CLOSED when FIN_ACK-packet is received

		Handles:
		- Wrong address
		- Invalid FIN-ACK packet
		- No FIN-ACK response
	'''
	def enter(self):
		'''
			Called when this state becomes current_state of State Machine

			Sends a FIN-packet to signal receiver, and for receiver to respond to.

			Also sets timeout for waiting
		'''
		super().enter()

		print("\n\nConnection Teardown:\n")

		# Setting timeout for recieving FIN-ACK
		self.parent.net_socket.settimeout(TIMEOUT)

		# Sending FIN-packet
		fin_packet = create_packet(b'', 0, 0, 2, 0)
		self.parent.net_socket.sendto(fin_packet, self.parent.counterpart_address)
		print("FIN packet is sent")


	def exit(self):
		'''
			Called when this state is changed away from by State Machine

			Resets timeout
		'''
		# Resetting timeout
		self.parent.net_socket.settimeout(None)


	def process(self):
		'''
			The "running" function call of the state

			Await FIN_ACK-packet from receiver and signal changing state to CLOSED
			
			Handles:
			- No FIN-ACK response for MAX_ATTEMPTS timeouts

			 (check_fin_ack_packet):
			- Wrong address of FIN-ACK packet 
			- Invalid FIN-ACK packet
			
		'''
		attempts = 0

		# Await FIN_ACK packet
		while True:
			try:
				# Receiving FIN-ACK packet from server
				fin_ack_packet, recieved_address = self.parent.net_socket.recvfrom(1024)
				
				if self.check_fin_ack_packet(fin_ack_packet, recieved_address):
					print("FIN-ACK packet is recieved")

					# Shutting down
					return self.parent.closedState

				else:
					continue

			except TimeoutError:
				if (attempts >= MAX_ATTEMPTS):
					# Shutting down if max attempts
					print("Max attempts for waiting for FIN_ACK-packet of handshake")

					return self.parent.closedState
				
				print("Waiting for FIN_ACK packet timed out. Retrying")
				attempts += 1
				continue
				
			except Exception as e:
				print(f"Error waiting for FIN_ACK from server: {e}")
				return self.parent.closedState
		# Waiting for FIN-ACK packet from server
		

	def check_fin_ack_packet(self, fin_ack_packet, recieved_address) -> bool:
		'''
			Validate FIN_ACK-packet

			Arguments
			fin_ack_packet: packet to validate
			received_address: sender-address of packet received

			Returns
			boolean: Wether or not packet is valid.

			Handles:
			- Wrong address of FIN-ACK packet
			- Invalid FIN-ACK packet
		'''
		data, _seq_num, _ack_num, flags, _window_size = dismantle_packet(fin_ack_packet)
		
		if recieved_address != self.parent.counterpart_address:
			return False

		if flags == 6 and len(data) == 0:
			# FIN-ACK packet received
			return True

		else:
			print(f"Error: Invalid FIN-ACK packet received")
			return False
		

