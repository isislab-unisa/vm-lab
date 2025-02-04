from enum import Enum


class Role(Enum):
	ADMIN = 'admin'
	MANAGER = 'manager'
	SIDEKICK = 'sidekick'
	NEW_USER = 'new_user'

	def to_phrase(self):
		"""Converts this role enum to a presentable phrase."""
		return self.value.replace("_", " ").capitalize()

	@staticmethod
	def from_phrase(phrase: str):
		"""Converts a presentable phrase into an equivalent role enum."""
		return Role(phrase.lower().replace(" ", "_"))
