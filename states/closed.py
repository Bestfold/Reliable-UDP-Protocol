import sys
from socket import *
from .state import State

class ClosedState(State):
	def __init__(self, name, parent):
		super().__init__(name, parent)
		self.first_run = True


	def enter(self):
		super().enter()

		# If returned here "from service", shut down
		if not self.first_run:
			print("Closing down...")
			if self.parent.net_socket:
				self.parent.net_socket.close()
			sys.exit(1)


	def exit(self):
		self.first_run = False


	def process(self):
		# Readability
		net_socket = self.parent.net_socket
		args = self.parent.args

		# If server is chosen, change state to ListenState
		if args.server:
			return self.parent.listenState
		
		# If client is chosen, change state to SynSentState
		elif args.client:
			return self.parent.synSentState