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
	
		State transfers:
		- LISTEN if --server is chosen at launch
		- SYN_SENT if --client is chosen at launch

	'''
	def __init__(self, name, parent):
		'''
			Called when initializing state instance.

			Sets first_run to True, which is used in enter()
		'''
		super().__init__(name, parent)
		self.first_run = True


	def enter(self):
		'''
			Called when this state becomes current_state of State Machine

			If this state is entered for the second time, it means it has 
			returned "from service", and the program will be shut down.
		'''
		super().enter()

		# If returned here "from service", shut down
		if not self.first_run:
			print("\nConnection closes...\n")
			if self.parent.net_socket:
				self.parent.net_socket.close()
			sys.exit(1)


	def exit(self):
		'''
			Called when this state is changed away from by State Machine

			Sets first_run to False since if state is entered for second
			time, it will shut down program.
		'''
		# Once moving out of ClosedState, is considered "in service"
		self.first_run = False


	def process(self):
		'''
			The "running" function call of the state

			Decides which state is next based on provided -s or -c
		'''
		# Readability
		args = self.parent.args

		# If server is chosen, change state to ListenState
		if args.server:
			return self.parent.listenState
		
		# If client is chosen, change state to SynSentState
		elif args.client:
			return self.parent.synSentState
