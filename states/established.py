from .state import State

class EstablishedState(State):
	def enter(self):
		super().enter()

	def exit(self):
		pass

	def process(self):
		pass