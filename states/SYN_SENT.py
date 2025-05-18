from socket import *
from drtpPacket import *
from .state import State

TIMEOUT = 0.4 # 400ms
MAX_ATTEMPTS = 5

class SynSentState(State):
	'''
		Send SYN-packet and await SYN_ACK 
	
		State transfers:
			- ESTABLISHED when SYN_ACK is received
			- CLOSED for program-breaking exceptions
		
	'''
	def enter(self):
		'''
			Called when this state becomes current_state of State Machine

			Send SYN packet

			And instantiate "global" variables to this run-instance's State Machine
			- Instantiate socket
			- Address of the correct receiver
			
			Also sets timeout for this state.
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
		self.parent.net_socket.sendto(syn_packet, (args.ip, args.port))
		print("\nSYN packet is sent")

		# Updating counterpart_address as the server address
		self.parent.counterpart_address = (args.ip, args.port)


	def exit(self):
		'''
			Called when this state becomes current_state of State Machine

			Resets timer
		'''
		# Reset timeout
		self.parent.net_socket.settimeout(None)


	def process(self):
		'''
			The "running" function call of the state

			Await SYN_ACK packet.

			Read data to self.parent.file

			Handles:
			- Timeout waiting for SYN_ACK
			- validating SYN_ACK (see check_syn_ack_packet() )
		'''

		# Reads self.parent.args.file
		# And saves data to self.parent.file
		# Handles exceptions
		if not self.read_file():
			return self.parent.closedState
		
		# Readability
		args = self.parent.args

		attempts = 0
		syn_ack_packet = None

		# Await SYN_ACK packet
		while True:
			try:
				# Receiving SYN-ACK packet from server
				syn_ack_packet, recieved_address = self.parent.net_socket.recvfrom(1024)
				
				if self.check_syn_ack_packet(syn_ack_packet, recieved_address):
					print("SYN_ACK packet is recieved")

					server_window_size = get_window(syn_ack_packet)

					# Set overall window size to minimum of recieved and argument provided size
					self.parent.effective_window_size = min(server_window_size, args.window)
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
			

			
	def check_syn_ack_packet(self, syn_ack_packet, recieved_address) -> bool:
		'''
			Local function to check if packet is correct SYN_ACK-packet
			Checks for:
			- correct address, 
			- flags
			- data size (should be 0)

			Arguments: 
			syn_ack_packet: packet to check
			recieved_address: address of recieved packet to check

			Returns:
			boolean: whether or not packet is valid
		'''

		# If not from the right address
		if recieved_address != self.parent.counterpart_address:
			return False
		
		data, _seq_num, _ack_num, flags, _window_size = dismantle_packet(syn_ack_packet)

		# Ignores other packets than SYN ACK
		if flags == 12 and len(data) == 0:
			return True
		else:
			print("Invalid ACK packet received")
			return False
		

	def read_file(self):
		'''
			Function to read a file, and check if it can read the file.
			When read correctly, it saves the data to file variable of State Machine
		'''
		try:
			# Filepath
			file_path = self.parent.args.file

			with open(file_path, 'rb') as found_file:
				data = found_file.read()
				self.parent.file = data
				return True
			
		except FileNotFoundError:
			print(f"File not found: {file_path}")
			return False

		except Exception as e:
			print(f"Error reading file: {e}")
			return False
		