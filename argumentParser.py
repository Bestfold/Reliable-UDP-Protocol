import argparse
import sys
import re


def get_args():
	try:
		parser = argparse.ArgumentParser(description='Reliable Transport Protocol on top of UDP')

		# Adding command line arguments for app
		parser.add_argument('-s', '--server', action='store_true', help='Run as server (default: False)')

		parser.add_argument('-c', '--client', action='store_true', help='Run as client (default: False)')

		parser.add_argument('-i', '--ip', type=str, default='127.0.0.1', 
				help='IP address to connect to (default: 127.0.0.1)')
		
		parser.add_argument('-p', '--port', type=int, default=8080, 
				help='Port number to listen on (server) or connect to (client )(default: 8080)')
		
		parser.add_argument('-f', '--file', type=str, default='PepsiGro.jpg', 
				help='Name of file to send (default: PepsiGro.jpg) Ignored on server')
		
		parser.add_argument('-w', '--window', type=int, default=3, 
				help='Sliding window size (default: 3) Ignored on server')
		
		parser.add_argument('-d', '--discard', type=int, default=100000, 
				help='Discard packet nr. provided. For testing purposes (defgault: 100000) Ignored on client')
		
		
		args = parser.parse_args()

		# Checks for critical errors in arguments. Exits program if any found
		error_check_args(args)
		
	except Exception as e:
		print(f'Error: {e}')
		sys.exit(1)

	return args



def error_check_args(args):
	'''
		Function to check for critical errors in the command line arguments.
		Exits program if errors found.
		Checks for:
		- Server AND client chosen
		- Neither server NOR client chosen
		- Invalid IP address (regex)
		- Invalid port number
		- Invalid window size
		- Invalid discard packet number
	
		Arguments: parsed argument object from argparse
		
	'''
	# Refex which allows desimal formatted IP address
	regexIp = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'

	# Handling errors in arguments
	if args.server and args.client:
		print('Error: Cannot run as both server and client.')
		raise Exception('Error: Cannot run as both server and client.')
	
	elif not args.server and not args.client:
		raise Exception('Error: Must run as either server or client. (-s or -c)')
	
	elif re.match(regexIp, args.ip) is None:
		raise Exception('Error: Invalid IP address. Format should be xxx.xxx.xxx.xxx, example: 192.0.168.3')

	elif args.port < 1024 or args.port > 65535:
		raise Exception('Error: Port number must be between 1024 and 65535.')

	elif args.window < 1:
		raise Exception('Error: Window size must be at least 1.')
		
	elif args.discard < 0:
		raise Exception('Error: Discard packet number must be a positive integer.')