class NotFoundError(Exception):
	def __init__(self, what):
		self.message = f"{what} not found."
		super().__init__(self.message)

	def __str__(self):
		return f"{self.message}"
