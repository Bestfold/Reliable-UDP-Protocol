import sys;
from server import *;
from client import *;
from socket import *;
from collections import deque;
from statemachine import StateMachine
from states import *

def main():
	'''
		S
	'''
	# Parse cli arguments and error check them
	args = get_args()

	net_socket: socket = None

	state_machine = StateMachine(args, net_socket)

	while(True):
		state_machine.process_state()

	'''
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
	'''
	

if __name__ == '__main__':
	main()