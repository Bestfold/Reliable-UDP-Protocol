from socket import *;
from drtpPacket import *;
from argumentParser import *;
from collections import deque;
import sys;

TIMEOUT = 0.4 # 400ms timeout for socket operations
MAX_ATTEMPTS = 5 # 5 attempts for resending packets for SYN and resending lost packets

def client(args):
	'''
		Client function to handle outgoing connections and data.
		Arguments: parsed argument object from argparse
	'''
	client_socket = socket(AF_INET, SOCK_DGRAM)
	client_socket.settimeout(TIMEOUT)

	arg_address = (args.ip, args.port)
	arg_window = args.window
	arg_file = args.file

	file = read_file(arg_file)
	print(f"File to send: {arg_file}")
	print(f"File size: {len(file)} bytes")

	# Initiate handshake with server
	server_window = connection_establishment(client_socket, arg_address, arg_window)
	print(f"Server window size: {server_window}")

	transfer_file(client_socket, arg_address, arg_window, server_window, file)

	connection_teardown(client_socket, arg_address, arg_window)
	# Exits program in function


def connection_establishment(client_socket, arg_address, arg_window):
	'''
		Function to perform a handshake with the server.
		Sends SYN packet and waits for SYN-ACK packet.
		If SYN-ACK packet received, send ACK packet.

		If no SYN-ACK packet when timeout, resend SYN packet up to 5 times.
		Exits program if no SYN-ACK packet received after 5 attempts.
		Exits program if invalid SYN-ACK packet received.

		Arguments: client socket, server IP and port, and window size

		Returns: Windows size of the server and the connected address

	'''
	attempts = 0
	while True:
		try:
			# Sending SYN packet to server
			syn_packet = create_packet(b'', 0, 0, 8, arg_window)
			client_socket.sendto(syn_packet, arg_address)
			print(f"Sent SYN packet to server {arg_address[0]}:{arg_address[1]}")

			# Receiving SYN-ACK packet from server
			syn_ack_packet, server_address = client_socket.recvfrom(1024)
			_data, seq_num, ack_num, flags, server_window = dismantle_packet(syn_ack_packet)

			# Ignores other packets than SYN ACK
			if flags != 12:
				continue
			
			print(f"Received SYN-ACK packet from server {arg_address[0]}:{arg_address[1]}")

			# Sending ACK packet to server
			ack_packet = create_packet(b'', seq_num, ack_num, 4, arg_window)
			client_socket.sendto(ack_packet, server_address)
			print(f"Sent ACK packet to server {server_address}")

			return server_window


		except TimeoutError:
			print("Error: Timeout while waiting for SYN-ACK packet.")
			if attempts >= MAX_ATTEMPTS:
				print("Max attempts reached. Exiting...")
				client_socket.close()
				sys.exit(1)
			attempts += 1
			continue
			
		except Exception as e:
			print(f"Error connecting to server: {e}")
			client_socket.close()
			sys.exit(1)


def transfer_file(client_socket, arg_address, arg_window, server_window, file):
	'''
		Transfer file data reliably. File is sent with drtp packets with a max size of 1000 
		bytes, 8 of which is the drtp header. The file data is then sent 992 bytes at a time.


	'''
	# Byte pointers that move with the already sent data.
	startByte = 0
	endByte = min(MAX_DATA, len(file))
	ack_num = 0 #TODO
	seq_num = 0

	# Calculate window size
	window_size = min(arg_window, server_window)
	# Deque of unacked packets of size calculated above
	unacked_window = deque((), window_size)
	
	attempts = 0

	while(True):
		# Sending packets when space in window.
		while(len(unacked_window) < unacked_window.maxlen):

			# Finish file transfer if no more bytes
			if len(file) < endByte: # TODO nylig endra til < fra <=
				break	

			print("DEBUG. Sender pga. åpent window")

			# even if endByte is out of bounds, its just the available data that is taken
			packet_data = file[startByte:endByte] 

			# Calculate sequence number dynamically
			seq_num += 1

			data_packet = create_packet(packet_data, seq_num, ack_num, 0, arg_window)
			client_socket.sendto(data_packet, arg_address)

			unacked_window.append(data_packet)

			startByte = endByte
			endByte = endByte + MAX_DATA # MAX_DATA from drtpPacket = 992 (bytes)

			print(f"Sent data packet to server {arg_address[0]}:{arg_address[1]}. seq: {seq_num}, len: {len(packet_data)}\n")

		
		
		# Recieving ACK packets:
		while(len(file) >= ack_num * MAX_DATA):
			try:
				# Finish when last ACK for file data is acquired
				# Also breaking after correct ACK recieved, to accomodate sending more data

				# Receiving ACK packet from server
				print("DEBUG. Waiting for ACK")
				ack_packet, server_address = client_socket.recvfrom(1024)
				# Ignoring from wrong address
				if server_address != arg_address:
					continue

				_data, _seq_num, recieved_ack_num, flags, _window_size = dismantle_packet(ack_packet)
				# Ignoring non-ACK addresses
				if flags != 4:
					continue
				
				# Seq number of first packet in window
				first_window_seq = get_seq_num(unacked_window[0])

				# Packet is the correct in order ACK
				if (recieved_ack_num == first_window_seq + 1):
					
					print(f"Received ACK packet from server {arg_address[0]}:{arg_address[1]}. ack: {recieved_ack_num}")

					ack_num = first_window_seq + 1
					# Remove packet from window
					unacked_window.popleft()
					break

			except(TimeoutError):
				print("RTO occured, attempts:", attempts)
				if attempts >= MAX_ATTEMPTS:
					print("Max attempts to resend packet after RTO. Closing down...")
					client_socket.close()
					sys.exit()

				attempts += 1

				resend_packet = unacked_window[0]
				_data, resend_seq_num, resend_ack_num, _flags, _window_size = dismantle_packet(resend_packet)
				client_socket.sendto(resend_packet, arg_address)
				
				print(f"Resending packet with seq: {resend_seq_num}, ack: {resend_ack_num}")
				continue
			
		# Finish file transfer if last ACK acquired
		if len(file) <= ack_num * MAX_DATA:
			print("ACK NUM: ", ack_num)
			print("ACK NUM * MAX_DATA: ", ack_num * MAX_DATA)
			print("FILE: ", len(file))
			break
		
	

def connection_teardown(client_socket, arg_address, arg_window):
	'''
		DRTP Teardown of reliable connection.
	'''
	# Sending FIN packet to server
	fin_packet = create_packet(b'', 0, 0, 2, arg_window)
	client_socket.sendto(fin_packet, arg_address)
	print(f"Sent FIN packet to server {arg_address[0]}:{arg_address[1]}")

	# Waiting for FIN-ACK packet from server
	fin_ack_packet, server_address = client_socket.recvfrom(1024)
	_data, _seq_num, _ack_num, flags, _window_size = dismantle_packet(fin_ack_packet)

	if flags != 6: #TODO SJEKK RIKTIG ADDREESSE
		# Invalid FIN-ACK packet received
		print(f"Error: Invalid FIN-ACK packet received. Wrong flag: {flags}")
		client_socket.close()
		sys.exit(1)

	print(f"Received FIN-ACK packet from server {server_address}")
	print("Tearing down connection...")
	client_socket.close()
	print("Conneciton torn down. Closing application.")
	sys.exit(0)
	

def read_file(file_path):
	'''
		Function to read a file and return its contents.
		Arguments: file path to be read
	'''
	try:
		with open(file_path, 'rb') as file:
			data = file.read()
			return data
		
	except FileNotFoundError:
		print(f"File not found: {file_path}")
		sys.exit(1)

	except Exception as e:
		print(f"Error reading file: {e}")
		sys.exit(1)