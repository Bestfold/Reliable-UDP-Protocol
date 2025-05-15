import sys
from socket import *
from .state import State

class ClosedState(State):
	'''
		Inital state and final state.

		Initial:
			Server goes to ListenState
			Client goes to SynSentState
		
		Final
			When connection is told to close, this state
			closes socket and exits program

	'''
	def __init__(self, name, parent):
		super().__init__(name, parent)
		self.first_run = True


	def enter(self):
		super().enter()

		# If returned here "from service", shut down
		if not self.first_run:
			print("\nConnection closes...\n")
			if self.parent.net_socket:
				self.parent.net_socket.close()
			sys.exit(1)


	def exit(self):
		# Once moving out of ClosedState, is considered "in service"
		self.first_run = False


	def process(self):
		# Readability
		args = self.parent.args

		# If server is chosen, change state to ListenState
		if args.server:
			return self.parent.listenState
		
		# If client is chosen, change state to SynSentState
		elif args.client:
			return self.parent.synSentState
