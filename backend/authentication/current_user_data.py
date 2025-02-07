from backend import Role
from utils.session_state import get_session_state_item


def get_current_user_role() -> Role | None:
	"""Retrieves the role of the user if it is logged-in, otherwise it will return `None`."""
	role_str = get_session_state_item('roles')
	if role_str:
		return Role(role_str)
	else:
		return None


def get_current_user_full_name() -> str | None:
	"""Retrieves the role of the user if it is logged-in, otherwise it will return `None`."""
	return get_session_state_item('name')


def get_current_user_name() -> str | None:
	"""Retrieves the username of the user if it is logged-in, otherwise it will return `None`."""
	return get_session_state_item("username")


def get_current_user_email() -> str | None:
	"""Retrieves the email of the user if it is logged-in, otherwise it will return `None`."""
	return get_session_state_item("email")


def is_logged_in() -> bool:
	"""Check whether the user is logged in or not."""
	if get_session_state_item('authentication_status'):
		return True
	else:
		# Status is None or False
		return False
