from .state import State

class LastAckState(State):
	def enter(self):
		super().enter()

	def exit(self):
		pass

	def process(self):
		pass