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

	# Empty socket to fill out within States
	net_socket: socket = None

	# Handling all states
	state_machine = StateMachine(args, net_socket)

	while(True):
		state_machine.process_state()


if __name__ == '__main__':
	main()