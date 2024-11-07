import streamlit as st
from streamlit import switch_page

from backend.authentication import is_logged_in, get_authenticator_object
from frontend.page_names import PageNames
from frontend.page_options import page_setup
from utils.session_state import get_session_state, pop_session_state

page_setup(title="Login", is_restricted=False)

if is_logged_in():
	# Correct credentials or already logged in
	switch_page(PageNames.my_vms)

authenticator = get_authenticator_object()

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