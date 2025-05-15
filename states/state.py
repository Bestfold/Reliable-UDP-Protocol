class State:

	def __init__(self, name, parent):
		self.name = name
		self.parent = parent
	
	def enter(self):
		#print("State entered:", self.name)
		pass

	def exit(self):
		pass

	def process(self):
		pass