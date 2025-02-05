import streamlit as st

from frontend import page_setup, PageNames
from frontend.components import error_message

from utils.session_state import get_session_state_item, pop_session_state_item


################################
#            SETUP             #
################################

psd = page_setup(
	title=PageNames.LOGIN.label,
	access_control="unregistered_only",
)


################################
#             PAGE             #
################################

try:
	st.cache_data.clear() # Clear cache to refresh table data
	psd.authenticator.login()
except Exception as e:
	error_message(unknown_exception=e)
else:
	if get_session_state_item('registration-success'):
		# Redirected here when the registration is successful
		st.success('Registration successful')
		pop_session_state_item('registration-success')

	if get_session_state_item('username-change-success'):
		# Redirected here when the username change is successful
		st.success(f"Username changed successfully changed")
		pop_session_state_item('username-change-success')

	if get_session_state_item('authentication_status') is None:
		# Standard message
		st.warning('Please type your credentials')
	elif get_session_state_item('authentication_status') is False:
		# Incorrect Credentials error message
		st.error('Incorrect credentials')