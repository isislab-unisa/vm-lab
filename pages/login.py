import streamlit as st

from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state_item, pop_session_state_item

authenticator = page_setup(
	title="Login",
	access_control=AccessControlType.UNREGISTERED_ONLY,
)

try:
	st.cache_data.clear() # Clear cache to refresh table data
	authenticator.login()
except Exception as e:
	st.error(e)
else:
	if get_session_state_item('registration-success'):
		st.success('Registration successful')
		pop_session_state_item('registration-success')

	if get_session_state_item('username-change-success'):
		st.success(f"Username changed successfully changed")
		pop_session_state_item('username-change-success')

	if get_session_state_item('authentication_status') is None:
		st.warning('Please type your credentials')
	elif get_session_state_item('authentication_status') is False:
		st.error('Credentials incorrect')