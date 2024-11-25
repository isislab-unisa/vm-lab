from streamlit import session_state


def get_session_state_item(key: str):
	"""Returns the value of a given key in the session state or `None` if not found."""
	if key not in session_state:
		return None
	else:
		return session_state[key]


def get__all_session_state_items() -> dict:
	"""Returns the session_state dictionary."""
	return session_state


def set_session_state_item(key: str, value):
	"""Sets the value of a given key in the session state."""
	session_state[key] = value


def pop_session_state_item(key: str):
	"""Removes and returns a given key from the session state."""
	if key not in session_state:
		return None
	else:
		return session_state.pop(key)