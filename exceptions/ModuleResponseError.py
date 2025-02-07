class ModuleResponseError(Exception):
	def __init__(self, message, module_name):
		self.message = message
		self.module_name = module_name
		super().__init__(self.message)

	def __str__(self):
		return f"The {self.module_name} has encountered an error: {self.message}"
