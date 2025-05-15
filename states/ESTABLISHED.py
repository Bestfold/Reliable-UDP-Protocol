from socket import *
from drtpPacket import *
from datetime import datetime
from collections import deque;
from .state import State

CLIENT_TIMEOUT = 0.4 # 400ms for client waiting for ACK
SERVER_TIMEOUT = 10 # 10s for server waiting for data
MAX_ATTEMPTS = 5

class EstablishedState(State):
	'''
		Data transfer (client) and data reception (server)

		Using sliding window for flow control

		Calculates throughput of data transfer

		Handles:
		- wrong address

		- invalid data packet
		- out-of-order data packet
		- duplicate data packet

		- invalid ACK packet
		- out-of-order ACK packet
	'''
	def enter(self):
		super().enter()

		# Send final ACK of handshake if client
		if self.parent.args.client:
			self.send_ack()
			# CLIENT_TIMEOUT for client
			self.parent.net_socket.settimeout(CLIENT_TIMEOUT)

		elif self.parent.args.server:
			# Coutns amount of bytes recieved
			self.total_bytes_recieved = 0

			# SERVER_TIMEOUT for client
			self.parent.net_socket.settimeout(SERVER_TIMEOUT)


	def exit(self):
		# Reset timemout
		self.parent.net_socket.settimeout(None)

		# Calculate throughput for data recieved by server
		if self.parent.args.server:

			# Duration of data reception in seconds
			duration = (self.end_time - self.start_time).total_seconds()

			# Total amount of bits recieved over transfer
			bits_recieved = self.total_bytes_recieved * 8

			# bits converted to Megabit by dividing by 1 million
			# which is then divided by total seconds   (b / 1_000_000) / s = Mbps
			# Printed in LastAckState
			mbps = (bits_recieved / 1_000_000) / duration

			self.parent.throughput = mbps



	def process(self):
		if self.parent.args.server:
			return self.server()
		elif self.parent.args.client:
			return self.client()

	
	def server(self):
		'''
			Awaits data packets and sends ACK packets in return to sender
			When a FIN packet is recieved, begin connection termination

			Exception handling:
				- TimeoutError when waiting for data packets from client after SERVER_TIMEOUT
				- Other exception when recieving data packets from server.

			Testing:
				Discards packet with sequence number equal to args.discard
				set as argument.
				(helper function)
		'''
		print("Recieving data:\n")

		# Start time of data transfer
		self.start_time = datetime.now()

		# Keeps a record of what sequence number has been recieved
		sequence_order = 0
		
		while(True):
			try:
				packet, recieved_address = self.parent.net_socket.recvfrom(1024)

				# Check if FIN packet
				if self.check_fin_packet(packet, recieved_address):
					print(f"\n\nFIN packet is recieved")

					# End time of data transfer
					self.end_time = datetime.now()

					return self.parent.lastAckState


				# Check for correct data packet
				if self.check_data_packet(packet, recieved_address, sequence_order):
					seq_num = get_seq_num(packet)
					print(f"{datetime.now()} -- packet {seq_num} is received")

					# Add data to self.parent.file which will be written at end of connection
					self.parent.file += get_data(packet)

					# Increase the order of sequences to keep score of which have been recieved
					sequence_order += 1

					self.total_bytes_recieved += len(packet)

					ack_packet = create_packet(b'', seq_num, seq_num + 1, 4, self.parent.effective_window_size)

					self.parent.net_socket.sendto(ack_packet, self.parent.counterpart_address)

					print(f"{datetime.now()} -- sending ack for the recieved {seq_num}")
				
				continue

			except TimeoutError:
				print(f"\nWaiting for data packets timed out after {SERVER_TIMEOUT} seconds.")
				return self.parent.closedState
			
			except Exception as e:
				print(f"Failed to recieve data packet from client. Exception: {e}")
				return self.parent.closedState 


	def client(self):
		'''
			Transfer file data reliably. File is sent with drtp packets with a max size of 1000 
			bytes, 8 of which is the drtp header. The file data is then sent 992 bytes at a time.

			Sends a new data packet whenever space in window and adds it to the window.
			When packet gets acked, it gets removed from the window, freeing up space
			for a new packet.

			If RTO waiting for ACK for a packet, resending ALL packets in window.

		'''
		# Byte pointer to where last data ended
		self.startByte = 0
		# Byte pointer to what current packet should contain
		self.endByte = min(MAX_DATA, len(self.parent.file))

		# Keeps order of sequence numbers that are sent
		self.seq_num_order = 0

		# Max size of sliding window. Calculated in handshake
		window_size = self.parent.effective_window_size

		# Sliding window. Using deque to allow for easy pop and append of packets
		sliding_window = deque((), window_size)
		
		attempts = 0

		# Is no ack recieved from server yet?
		no_ack_recieved = True

		print("Data transfer:\n")

		while(True):
			#print("File length: ", len(self.parent.file)) TODO
			#print("endByte: ", self.endByte) TODO
			# Creates and sends packets in correct order if available space in sliding window
			self.send_available_packets(sliding_window)
			#print("seq_num_order: ", self.seq_num_order) TODO
			
			# No more data to send and all sent packets acked
			if len(self.parent.file) < self.endByte and len(sliding_window) == 0:
				return self.parent.finWaitState
			
			# Recieving ACKs
			try:
				ack_packet, recieved_address = self.parent.net_socket.recvfrom(1024)

				# Check if valid ACK
				if self.check_ack_packet(ack_packet, recieved_address, sliding_window):
					no_ack_recieved = False

					print(f"{datetime.now()} -- ACK for packet = {get_seq_num(ack_packet)} is recieved")

					# First packet in sliding window now acked, so removing it
					sliding_window.popleft()

			except TimeoutError:
				print(f"{datetime.now()} -- RTO occured")
				
				# If no ack is recieved, assume last ACK of handshake got lost and resend
				if no_ack_recieved:
					self.send_ack()

				# Resends all packets in sliding window because of RTO
				self.resend_sliding_window(sliding_window)
			
	






	# Helper functions:








	def check_fin_packet(self, data_packet, recieved_address):
		'''
			Local function to check if packet is correct FIN-packet
			Checks for:
			- correct address, 
			- flags
			- data (should be 0)

			Arguments: 
			data_packet -> packet to check
			recieved_address -> address of recieved packet to check
		'''
		# If not from the right address
		if recieved_address != self.parent.counterpart_address:
			return False
		
		data, _seq_num, _ack_num, flags, _window_size = dismantle_packet(data_packet)

		if flags == 2 and len(data) == 0:
			return True
		else:
			return False
				

	def check_data_packet(self, data_packet, recieved_address, sequence_order):
		'''
			Local function to check if packet is correct data-packet
			Checks for:
			- correct address, 
			- duplicate
			- out-of-order
			- flags (should be 0)
			- discards packet with seq == discard argument

			Arguments: 
			data_packet -> packet to check
			recieved_address -> address of recieved packet to check
			sequence_order -> sequence order of the already arrived packets
		'''

		# If not from the right address
		if recieved_address != self.parent.counterpart_address:
			return False
		
		_data, seq_num, _ack_num, flags, _window_size = dismantle_packet(data_packet)

		# Discarding for testing purposes
		if seq_num == self.parent.args.discard:
			# Set to a high number
			self.parent.args.discard = 1_000_000
			return False

		if seq_num != (sequence_order + 1):
			print(f"{datetime.now()} -- out-of-order packet {seq_num} is recieved")
			return False

		if seq_num == sequence_order:
			print(f"{datetime.now()} -- duplicate packet {seq_num} is recieved")
			return False

		# Has correct flag of a data packet
		if flags == 0:
			return True
		else:
			print("Invalid data packet received")
			return False


	def send_available_packets(self, sliding_window):
		# Sending packets when space in window and still more data not sent in packets.
		while(len(sliding_window) < sliding_window.maxlen and len(self.parent.file) >= self.endByte): #TODO might be > and not >=

			# even if endByte is out of bounds, its just the available data that is taken
			packet_data = self.parent.file[self.startByte:self.endByte] 

			# Calculates sequence number dynamically
			self.seq_num_order += 1

			data_packet = create_packet(packet_data, self.seq_num_order, 0, 0, self.parent.effective_window_size)

			self.parent.net_socket.sendto(data_packet, self.parent.counterpart_address)

			# Adding unacked data packet to sliding window
			sliding_window.append(data_packet)

			self.startByte = self.endByte
			self.endByte += MAX_DATA # MAX_DATA from drtpPacket = 992 (bytes)

			print(f"{datetime.now()} -- packet with seq = {self.seq_num_order} is sent, sliding window = {self.seq_nums_in_window(sliding_window)}")


	def seq_nums_in_window(self, sliding_window) -> str:
		'''
			Returns a formatted string of each sequence number within the sliding window.
			Format: {3, 4, 5, 6}

			Argument:
			sliding_window -> the window to read each sequence number of packets

			Returns:
			string in format
		'''
		return "{" + ", ".join(str(get_seq_num(packet)) for packet in sliding_window) + "}"


	def check_ack_packet(self, ack_packet, recieved_address, sliding_window) -> bool:
		'''
			Local function to check if packet is correct ACK-packet
			Checks for:
			- correct address, 
			- flags
			- data size (should be 0)
			- In order sequence number

			Arguments: 
			ack_packet -> packet to check
			recieved_address -> address of recieved packet to check

			Returns:
			bool -> wether or not packet is valid ACK
		'''
		# If not from the right address
		if recieved_address != self.parent.counterpart_address:
			return False
			
		data, seq_num, _ack_num, flags, _window_size = dismantle_packet(ack_packet)

		# Out of order ACK
		if get_seq_num(sliding_window[0]) != seq_num:
			return False
			
		# Check for invalid ACK packet
		if flags == 4 and len(data) == 0:
			return True
		else:
			print("Invalid ACK packet received")
			return False
	

	def resend_sliding_window(self, sliding_window):
		'''
			Resends all packets in sliding window

			Argument:
			sliding_window -> window to resend packets from
		'''
		for packet in sliding_window:
			self.parent.net_socket.sendto(packet, self.parent.counterpart_address)
			print(f"{datetime.now()} -- retransmitting packet with seq = {get_seq_num(packet)}")


	def send_ack(self):
			'''
				Sends ACK as the final part of the initial handshake
			'''
			# Sending ACK packet to server
			ack_packet = create_packet(b'', 0, 0, 4, self.parent.effective_window_size)

			self.parent.net_socket.sendto(ack_packet, self.parent.counterpart_address)
			print(f"ACK packet is sent\nConnection Establishing\n")
