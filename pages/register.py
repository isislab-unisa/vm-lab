import streamlit as st
from streamlit import switch_page
from frontend.custom_forms import register_user

from backend.authentication import is_logged_in, get_authenticator_object
from frontend.page_names import PageNames
from frontend.page_options import page_setup
from utils.session_state import get_session_state, pop_session_state

page_setup(title="Register", is_restricted=False, print_session_state=True)

if is_logged_in():
	# Already logged in
	switch_page(PageNames.my_vms)

if get_session_state('registration_success'):
	pop_session_state('registration_success')
	switch_page(PageNames.login)

authenticator = get_authenticator_object()

# try:
# 	email_of_registered_user, \
# 	username_of_registered_user, \
# 	name_of_registered_user = authenticator.register_user(key="Test")
# 	if email_of_registered_user:
# 		st.success('User registered successfully')
# except Exception as e:
# 	st.error(e)

try:
	register_user()
except Exception as e:
	st.error(e)