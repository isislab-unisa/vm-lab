import streamlit as st

from frontend.custom_forms import change_username, change_email, change_password
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state

authenticator = page_setup(
	title="User Settings",
	print_session_state=True,
	access_control=AccessControlType.LOGGED_IN_ONLY
)

st.title("User Settings")
username = get_session_state("username")
email = get_session_state("email")

if username is None:
	st.error("Error, no username found")
else:
	change_username(username)

if email is None:
	st.error("Error, no email found")
else:
	change_email(email)

if username is None:
	st.error("Error, no username found")
else:
	change_password(username)



