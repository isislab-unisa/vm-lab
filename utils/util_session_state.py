from streamlit import session_state


def in_session_state(key: str):
	"""Check if a given key is in the session state"""
	return key in session_state