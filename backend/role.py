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


def role_has_enough_priority(current_role: Role, minimum_role_required: Role) -> bool:
	"""
	Checks whether a role has a sufficient priority level to meet a minimum role requirement.
	Where the admin has the highest priority level, while a new user has the lowest priority level.

	:param current_role: The current role
	:param minimum_role_required: The minimum required role
	:return: `True` if the role has sufficient (equal or greater) priority, `False` otherwise
	"""
	def to_priority(r) -> int:
		match r:
			case Role.ADMIN:
				return 0
			case Role.MANAGER:
				return 1
			case Role.SIDEKICK:
				return 2
			case Role.NEW_USER:
				return 3

	current_priority = to_priority(current_role)
	minimum_priority = to_priority(minimum_role_required)

	return current_priority <= minimum_priority


def role_in_white_list(current_role: Role, white_list: list[Role]) -> bool:
	"""
	Checks whether a role is present in a list of authorized roles.
	:param current_role: The current role
	:param white_list: A list of authorized roles
	:return: `True` if the role is present in a list of authorized roles, `False` otherwise
	"""
	return current_role in white_list