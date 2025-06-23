from struct import *;

# Global variables
header_format = '!HHHH' # Header format for DRTP packets

MAX_DATA = 992

# Function sourced from https://github.com/safiqul/2410/blob/main/header/header.py
def create_packet(data, seq_num, ack_num, flags, window_size):
	'''
		Function to package data into DRTP packets.
		
		Arguments: data to be packaged

		Returns: created packet
	'''
	header = pack (header_format, seq_num, ack_num, flags, window_size)

	packet = header + data

	return packet


def dismantle_packet(packet):
	'''
		Function to dismantle DRTP packets into header and data.
		
		Arguments: packet to be dismantled

		Returns:
		data: data of packet
		seq_num: sequence number of packet
		ack_num: acknowledgement number of packet
		flags: flags of packet
		window_size: window size set in packet
	'''
	header = packet[:calcsize(header_format)]
	data = packet[calcsize(header_format):]

	seq_num, ack_num, flags, window_size = unpack(header_format, header)

	# SYN = 8, ACK = 4, FIN = 2, RST = 1
	#flags = parse_flags(flags_in_bits)
	
	return data, seq_num, ack_num, flags, window_size


def get_seq_num(packet):
	'''
		Dismatles packet and returns only sequence number

		Arguments: drtp packet

		Returns: sequence number of packet
	'''
	_data, seq_num, _ack_num, _flags, _window_size = dismantle_packet(packet)
	return seq_num


def get_ack_num(packet):
	'''
		Dismatles packet and returns only Acknowledge number

		Arguments: drtp packet

		Returns: acknowledgement number of packet
	'''
	_data, _seq_num, ack_num, _flags, _window_size = dismantle_packet(packet)
	return ack_num


def get_window(packet):
	'''
		Dismatles packet and returns only size of window in packet

		Arguments: drtp packet

		Returns: window size of packet
	'''
	_data, _seq_num, _ack_num, _flags, window_size = dismantle_packet(packet)
	return window_size


def get_data(packet):
	'''
		Dismatles packet and returns data in packet

		Arguments: drtp packet

		Returns: data of packet
	'''
	data, _seq_num, _ack_num, _flags, _window_size = dismantle_packet(packet)
	return data

# Function sourced from https://github.com/safiqul/2410/blob/main/header/header.py
def parse_header(header):
	'''
		Function to parse the header of a DRTP packet.
		
		Arguments: header to be parsed

		Returns: parsed header
	'''
	header_from_msg = unpack(header_format, header)
	return header_from_msg

# Function sourced from https://github.com/safiqul/2410/blob/main/header/header.py
def parse_flags(flags):
	'''
		Function to parse the flags of a DRTP packet.
		
		Arguments: flags to be parsed

		Returns: parsed flags
	'''
	# SYN = 8, ACK = 4, FIN = 2, RST = 1
	syn = flags & (1 << 3)
	ack = flags & (1 << 2)
	fin = flags & (1 << 1)
	rst = flags & (1 << 0)
	return syn, ack, fin, rst