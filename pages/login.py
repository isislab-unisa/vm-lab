import streamlit as st

from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state, pop_session_state

authenticator = page_setup(
	title="Login",
	access_control=AccessControlType.UNREGISTERED_ONLY,
	print_session_state=True
)

try:
	authenticator.login()
except Exception as e:
	st.error(e)
else:
	if get_session_state('registration-success'):
		st.success('Registration successful')
		pop_session_state('registration-success')
	if get_session_state('authentication_status') is None:
		st.warning('Please type your credentials')
	elif get_session_state('authentication_status') is False:
		st.error('Credentials incorrect')