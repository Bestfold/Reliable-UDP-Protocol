from socket import *
from drtpPacket import *
from .state import State

TIMEOUT = 0.4 # 400ms
MAX_ATTEMPTS = 5

class SynRecvdState(State):
	def enter(self):
		super().enter()
		# Address saved from SYN-packet recieved in LISTEN-State
		client_address = self.parent.counterpart_address

		# Set TIMEOUT for recieving ACK
		self.parent.net_socket.settimeout(TIMEOUT)

		# Send SYN-ACK packet to client
		syn_ack_packet = create_packet(b'', 0, 0, 12, self.parent.args.window)
		self.parent.net_socket.sendto(syn_ack_packet, client_address)
		print("SYN-ACK packet is sent")


	def exit(self):
		# Reset timeout
		self.parent.net_socket.settimeout(None)

	def process(self):
		'''
			Await ACK packet for handshake to be complete
			and connection established. Waiting until TIMEOUT
			for a total of MAX_ATTEMPTS tries. 
			
			If no more tries, shuts down connection throug CLOSED-state
		'''
		attempts = 0
		ack_packet = None

		
		# Waits for final ACK of handshake for a maximum of MAX_ATTEMPTS
		#  before returning CLOSED-state which shuts down connection
		while(True):
			try:
				# Wait for ACK packet from client
				ack_packet, recieved_address = self.parent.net_socket.recvfrom(1024)

				# Check for the right packet
				if self.check_ack_packet(ack_packet, recieved_address):
					print("ACK packet received. \nConnection Established\n")
					return self.parent.establishedState
				
				else:
					continue

			except TimeoutError:
				if (attempts >= MAX_ATTEMPTS):
					# Shutting down if max attempts
					print("Max attempts for waiting for final ACK of handshake")

					return self.parent.closedState
				
				print("Waiting for ACK packet timed out. Retrying")
				attempts += 1
				continue
				
			except Exception as e:
				print(f"Error waiting for final ACK from client: {e}")
				return self.parent.closedState
		


	def check_ack_packet(self, ack_packet, recieved_address) -> bool:
		'''
			Local function to check if packet is correct ACK-packet
			Checks for:
			- correct address, 
			- flags
			- data size (should be 0)

			Arguments: 
			ack_packet -> packet to check
			recieved_address -> address of recieved packet to check
		'''
		# If not from the right address
		if recieved_address != self.parent.counterpart_address:
			return False
			
		data, _seq_num, _ack_num, flags, _window_size = dismantle_packet(ack_packet)
			
		# Check for invalid ACK packet
		if flags == 4 and len(data) == 0:
			return True
		else:
			print("Invalid ACK packet received")
			return False