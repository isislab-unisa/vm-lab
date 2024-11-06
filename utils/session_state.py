from streamlit import session_state


def in_session_state(key: str) -> bool:
	"""Check if a given key is in the session state"""
	return key in session_state


def get_session_state(key: str):
	"""Returns the value of a given key in the session state or None if not found"""
	if not in_session_state(key):
		return None
	else:
		return session_state[key]


def set_session_state(key: str, value):
	"""Sets the value of a given key in the session state"""
	session_state[key] = value


def pop_session_state(key: str):
	"""Removes and returns a given key from the session state"""
	if not in_session_state(key):
		return None
	else:
		return session_state.pop(key)