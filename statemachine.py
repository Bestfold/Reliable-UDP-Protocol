from states import *;

class StateMachine:
	'''
		Finite State Machine to control the protocols different
		behaviours in accordance with states.

		State Machine handles changes between states and passes
		function calls down to each state.

		Every state has an instance here. State Machine changes
		which of the instances gets their functions called.
	'''

	def __init__(self, args, net_socket):
		'''
			Initialize State Machine. Also instantiates an instance of
			every state that the state machin can change between and pass
			its running to. Also passes itself as a parent refrence to 
			every state for them to interact with.

			Arguments:
			args -> arguments parsed by argumentParser
			net_socket -> uninstantiated socket to be instantiated in states
		'''
		# Parent variables for the states:
		self.args = args
		self.net_socket = net_socket
		
		# Holds the recieved address of the connection upon handshake
		self.counterpart_address = None

		# Holds size of window. Calculated for client
		self.effective_window_size = None

		# The current state of the State Machine
		self.current_state = None
		
		# Variable to keep file to send for client, and accumulate data to for server
		self.file = b''

		# Instantiating every state and passing parent refrence to them
		self.closedState = ClosedState("ClosedState", self)
		self.listenState = ListenState("ListenState", self)
		self.synRecvdState = SynRecvdState("SynRecvdState", self)
		self.synSentState = SynSentState("SynSentState", self)
		self.establishedState = EstablishedState("EstablishedState", self)
		self.closeWaitState = CloseWaitState("CloseWaitState", self)
		self.lastAckState = LastAckState("LastAckState", self)

		# Initial state = ClosedState
		self.change_state(self.closedState)


	def change_state(self, new_state: State):
		'''
			Handles changing of states. Passes the 
			enter() and exit() function call to the 
			current state.

			Called in process_state()

			Argument:
			new_state -> instance of state to change to
		'''
		if new_state and self.current_state:
			self.current_state.exit()

		self.current_state = new_state
		self.current_state.enter()


	def process_state(self):
		'''
			Passes the "driving" function call down
			to the current state.

			If the process() in the curret_state returns
			another instance of a state, it changes
			state to the new state.
		'''
		#print(self.current_state.name)
		new_state = self.current_state.process()
		if new_state:
			self.change_state(new_state)