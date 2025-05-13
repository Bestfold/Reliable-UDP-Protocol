class State:

	def __init__(self, name, parent):
		self.name = name
		#self.args = parent.args
		#self.net_socket = parent.net_socket
		self.parent = parent
	
	def enter(self):
		print("State entered:", self.name)

	def exit(self):
		pass

	def process(self):
		pass