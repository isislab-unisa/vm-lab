import streamlit as st

from frontend.custom_forms.authentication import register_user
from frontend.page_options import page_setup, AccessControlType

page_setup(
	title="Register",
	access_control=AccessControlType.UNREGISTERED_ONLY,
)

try:
	# TODO: limit the registration attempts to 5-6 captcha errors
	register_user()
except Exception as e:
	st.error(e)