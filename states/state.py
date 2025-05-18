from abc import ABC, abstractmethod

class State(ABC):
	'''
		Abstract State class
	'''

	def __init__(self, name, parent):
		'''
			Initialization
		'''
		self.name = name
		self.parent = parent
	
	@abstractmethod
	def enter(self):
		'''
			Called when inheriting state becomes current_state of State Machine
		'''
		#print("State entered:", self.name)
		pass

	@abstractmethod
	def exit(self):
		'''
			Called when inheriting state becomes current_state of State Machine
		'''
		pass
	
	@abstractmethod
	def process(self):
		'''
			The "running" function call of the inheriting state
		'''
		pass