from .states import *;

class StateMachine:

	def __init__(self, args, net_socket):
		self.args = args
		self.net_socket = net_socket
		self.current_state = None

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
		if new_state and self.current_state:
			self.current_state.exit()

		self.current_state = new_state
		self.current_state.enter()


	def process_state(self):
		#print(self.current_state.name)
		new_state = self.current_state.process()
		if new_state:
			self.change_state(new_state)