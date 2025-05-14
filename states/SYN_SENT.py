from socket import *
from drtpPacket import *
from .state import State

TIMEOUT = 0.4 # 400ms
MAX_ATTEMPTS = 5

class SynSentState(State):
	def enter(self):
		'''
			Send SYN packet
		'''
		super().enter()

		# Readability
		args = self.parent.args

		# Setting socket to be IPv4, UDP
		self.parent.net_socket = socket(AF_INET, SOCK_DGRAM)

		# Set TIMEOUT for recieving ACK
		self.parent.net_socket.settimeout(TIMEOUT)
		
		# Creating SYN packet
		syn_packet = create_packet(b'', 0, 0, 8, args.window)

		# Sending SYN packet
		self.parent.net_socket.send(syn_packet, (args.ip, args.port))
		print("SYN-packet sent to", (args.ip, args.port))

		# Updating counterpart_address as the server address
		self.parent.counterpart_address = (args.ip, args.port)


	def exit(self):
		# Reset timeout
		self.parent.net_socket.settimeout(None)


	def process(self):
		'''
			Await SYN_ACK packet.
		'''
		# Readability
		args = self.parent.args

		attempts = 0
		syn_ack_packet = None

		# Await SYN_ACK packet
		while True:
			try:
				# Receiving SYN-ACK packet from server
				syn_ack_packet, recieved_address = self.parent.net_socket.recv(1024)

				if self.check_syn_ack_packet(syn_ack_packet, recieved_address, self.parent.counterpart_address):
					print("SYN_ACK packet recieved.")
					return self.parent.establishedState

				else:
					continue

			except TimeoutError:
				if (attempts >= MAX_ATTEMPTS):
					# Shutting down if max attempts
					print("Max attempts for waiting for SYN_ACK-packet of handshake")

					return self.parent.closedState
				
				print("Waiting for SYN_ACK packet timed out. Retrying")
				attempts += 1
				continue
				
			except Exception as e:
				print(f"Error waiting for SYN_ACK from server: {e}")
				return self.parent.closedState
			

			
	def check_syn_ack_packet(syn_ack_packet, recieved_address, server_address):
		'''
			Local function to check if packet is correct SYN_ACK-packet
		'''

		# If not from the right address
		if recieved_address != server_address:
			return False
		
		data, seq_num, ack_num, flags, window_size = dismantle_packet(syn_ack_packet)
		print(f"seq_num: {seq_num}, ack_num: {ack_num}, falgs: {flags}, Window size: {window_size}")

		# Ignores other packets than SYN ACK
		if flags == 12 and len(data) == 0:
			return True
		else:
			print("Invalid ACK packet received")
			return False	
		