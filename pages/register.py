import streamlit as st

from frontend.custom_forms import register_user
from frontend.page_options import page_setup, AccessControlType

authenticator = page_setup(
	title="Register",
	access_control=AccessControlType.UNREGISTERED_ONLY,
	print_session_state=True
)

try:
	# TODO: limit the registration attempts to 5-6 captcha errors
	register_user()
except Exception as e:
	st.error(e)