import streamlit as st

from frontend.custom_forms.authentication import register_user
from frontend.page_setup import page_setup

page_setup(
	title="Register",
	access_control="unregistered_only",
)

try:
	# TODO: limit the registration attempts to 5-6 captcha errors
	register_user()
except Exception as e:
	st.error(e)