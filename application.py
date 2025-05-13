import sys;
from server import *;
from client import *;
from collections import deque;

def main():
	'''
		S
	'''
	# Parse cli arguments and error check them
	args = get_args()

	if args.server:
		print('Setting up server')
		# Start server
		server(args)
	elif args.client:
		print('Setting up client')
		# Start client
		client(args)
	else:
		print('Error: Neither server nor client mode selected.')
		sys.exit(1)
	

if __name__ == '__main__':
	main()