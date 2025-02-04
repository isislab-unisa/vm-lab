from enum import Enum


class Role(Enum):
	ADMIN = 'admin'
	MANAGER = 'manager'
	SIDEKICK = 'sidekick'
	NEW_USER = 'new_user'

	def to_string(self):
		"""Converts this role enum to its value."""
		return self.value

	@staticmethod
	def from_string(role_str: str):
		"""Converts a string into an equivalent role enum."""
		match role_str:
			case Role.NEW_USER.value:
				return Role.NEW_USER
			case Role.SIDEKICK.value:
				return Role.SIDEKICK
			case Role.MANAGER.value:
				return Role.MANAGER
			case Role.ADMIN.value:
				return Role.ADMIN
			case _:
				return None

	def to_phrase(self):
		"""Converts this role enum to a presentable phrase."""
		return self.value.replace("_", " ").capitalize()

	@staticmethod
	def from_phrase(phrase: str):
		"""Converts a presentable phrase into an equivalent role enum."""
		match phrase.lower():
			case Role.ADMIN.value:
				return Role.ADMIN
			case Role.MANAGER.value:
				return Role.MANAGER
			case Role.SIDEKICK.value:
				return Role.SIDEKICK
			case _:
				return Role.NEW_USER

