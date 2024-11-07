from streamlit import session_state


def get_session_state(key: str):
	"""Returns the value of a given key in the session state or None if not found"""
	if key not in session_state:
		return None
	else:
		return session_state[key]


def get_session_state_all() -> dict:
	"""Returns the session_state dictionary"""
	return session_state


def set_session_state(key: str, value):
	"""Sets the value of a given key in the session state"""
	session_state[key] = value


def pop_session_state(key: str):
	"""Removes and returns a given key from the session state"""
	if key not in session_state:
		return None
	else:
		return session_state.pop(key)