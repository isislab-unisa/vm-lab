import streamlit as st
from streamlit import switch_page

from backend.authentication import is_logged_in, get_authenticator_object
from frontend.page_names import PageNames
from frontend.page_options import page_setup

page_setup(title="Register", is_restricted=False)

if is_logged_in():
	# Already logged in
	switch_page(PageNames.my_vms)

authenticator = get_authenticator_object()

try:
	email_of_registered_user, \
	username_of_registered_user, \
	name_of_registered_user = authenticator.register_user()
	if email_of_registered_user:
		st.success('User registered successfully')
except Exception as e:
	st.error(e)