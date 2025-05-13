from socket import *;
from drtpPacket import *;
from argumentParser import *;
import sys;

TIMEOUT = 5 # 5 second timeout for socket operations

def server(args):
	'''
		Server function to handle incoming connections and data.
		Arguments: parsed argument object from argparse

		Parts of the code is sourced from my previous assignments
	'''
	arg_ip = args.ip
	arg_port = args.port
	arg_window = args.window
	arg_discard = args.discard

	# Creating server socket with IPv4 (AF_INET) and UDP (SOCK_STREAM)
	server_socket = socket(AF_INET, SOCK_DGRAM)
	

	try:
		# Bind the socket to the server IP and port
		server_socket.bind((arg_ip, arg_port))
		print(f"Ready to serve on {arg_ip}:{arg_port}")

		while True:
			client_address = await_and_establish_connection(server_socket, arg_window)

			file_data = recieve_file(server_socket, arg_window, client_address, arg_discard)
			save_file(file_data)
			
	except KeyboardInterrupt:
		print('Server interrupted. Exiting...')
		server_socket.close()
		sys.exit(0)
	
	except Exception as e:
		print("Failer i server")
		print(f'Error: {e}')
		server_socket.close()
		sys.exit(1)

def recieve_file(server_socket, arg_window, client_address, arg_discard):
	'''
		Recieves a file from established connection.
		Using window.
		Takese packets until FIN packet is recieved.
		Arguments: server socket
	'''
	file = b''

	# Which sequence number last acked
	accumulated_seq = 0

	while True:
		packet, recieved_address = server_socket.recvfrom(1024)
		# Ingore packet if not from connected address
		if recieved_address != client_address:
			continue

		data, seq_num, ack_num, flags, _window_size = dismantle_packet(packet)


		if flags == 2:
			print("FIN packet recieved. Closing connection.")
			fin_ack_packet = create_packet(b'', seq_num, ack_num, 6, arg_window)
			server_socket.sendto(fin_ack_packet, client_address)
			print("Sent ACK packet to client")
			print("Connecion successfully torn down")

			return file

		elif flags == 0 and len(data) > 0:
			# Ignore out of order packet
			#print("Accum seq: ", accumulated_seq)
			#print("seq - 1: ", seq_num - 1)
			#if accumulated_seq != (seq_num - 1): #TODO
			#	continue

			print(f"Data packet recieved from {client_address}. seq: {seq_num} ")

			if arg_discard == seq_num:
				print(f"Discarding packet seq: {seq_num} for testing purposes")
				# Setting discard value to a huge number
				arg_discard = 100000
				continue

			file += data

			ack_num = seq_num + 1

			ack_packet = create_packet(b'', seq_num, ack_num, 4, arg_window)
			server_socket.sendto(ack_packet, client_address)

			#accumulated_seq = seq_num

			print(f"Packet seq: {seq_num}, len: {len(data)}, acked: {ack_num} (sent)")

		else:
			print(f"Error: Invalid packet received. Seq: {seq_num}, ack: {ack_num}")
			print(f"Flags: {flags}, Data: {data}")
			print("Closing connection.")
			server_socket.close()
			sys.exit(1)
			
			


def await_and_establish_connection(server_socket, arg_window):
	'''
		Function to greet the client and perform a handshake.
		Arguments: client socket, server IP and port, and window size
	'''
	print('Awaiting SYN packet...')
	syn_packet, client_address = server_socket.recvfrom(1024)
	print("From client:", client_address)

	# Unpack the header from the message
	data, seq_num, ack_num, flags, window_size = dismantle_packet(syn_packet)
	print(f'Sequence number: {seq_num}, Acknowledgment number: {ack_num}, falgs: {flags}, Window size: {window_size}')

	# Chech that SYN packet is correct
	if flags == 8 and len(data) == 0:
		print("SYN packet received. Sending SYN-ACK packet.")

		# Send SYN-ACK packet to client
		syn_ack_packet = create_packet(b'', seq_num, ack_num, 12, arg_window)
		server_socket.sendto(syn_ack_packet, client_address)
		print(f"Sent SYN-ACK packet to {client_address}")
	
		# Wait for ACK packet from client
		server_socket.settimeout(TIMEOUT)
		ack_packet, _recieved_address = server_socket.recvfrom(1024)
		server_socket.settimeout(None)

		data, seq_num, ack_num, flags, window_size = dismantle_packet(ack_packet)

		print(f'Sequence number: {seq_num}, Acknowledgment number: {ack_num}, falgs: {flags}, Window size: {window_size}')
		if flags == 4 and len(data) == 0:
			print("ACK packet received. Handshake complete.")
			return client_address
		else:
			print("Invalid ACK packet received")
			print("Exiting...")
			server_socket.close()
			sys.exit(1)


def save_file(file_data):
	'''
		Takes byte data of file and writes to filestructure

		Arguments: variable containing bytes of file
	'''
	try:
		with open('recieved_data.jpg', 'wb') as new_file:
			new_file.write(file_data)

	except Exception as e:
		print(f"Error reading file: {e}")
		sys.exit(1)