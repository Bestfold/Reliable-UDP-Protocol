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
		print(f"Sent SYN-ACK packet to {client_address}")


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
				if self.check_ack_packet(ack_packet, recieved_address, self.parent.counterpart_address):
					print("ACK packet received. Handshake complete.")
					return self.parent.EstablishedState
				
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
		


	def check_ack_packet(ack_packet, recieved_address, client_address) -> bool:
		'''
			Local function to check if packet is correct ACK-packet
		'''
		# If not from the right address
		if recieved_address != client_address:
			return False
			
		data, seq_num, ack_num, flags, window_size = dismantle_packet(ack_packet)
		print(f"seq_num: {seq_num}, ack_num: {ack_num}, falgs: {flags}, Window size: {window_size}")
			
		# Check for invalid ACK packet
		if flags == 4 and len(data) == 0:
			return True
		else:
			print("Invalid ACK packet received")
			return False