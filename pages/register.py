import streamlit as st
from streamlit import switch_page
from streamlit_authenticator import RegisterError

from frontend.custom_forms import register_user

from backend.authentication import is_logged_in, get_authenticator_object
from frontend.page_names import PageNames
from frontend.page_options import page_setup
from utils.session_state import get_session_state, pop_session_state

page_setup(title="Register", is_restricted=False)

if is_logged_in():
	# Already logged in
	switch_page(PageNames.my_vms)

try:
	# TODO: limit the registration attempts to 5-6 captcha errors
	register_user()
except Exception as e:
	st.error(e)