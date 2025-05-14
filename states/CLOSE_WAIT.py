from .state import State

class CloseWaitState(State):
	def enter(self):
		super().enter()

	def exit(self):
		pass

	def process(self):
		pass