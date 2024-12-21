import streamlit as st

from frontend.page_options import page_setup, AccessControlType
from frontend.custom_forms.user_details import change_username, change_email, change_password, change_first_last_name
from utils.session_state import get_session_state_item

page_setup(
	title="User Settings",
	access_control=AccessControlType.LOGGED_IN_ONLY
)

st.title("User Settings")
username = get_session_state_item("username")
email = get_session_state_item("email")
first_last_name = get_session_state_item("name")

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

if username is None:
	st.error("Error, no username found")
elif first_last_name is None:
	st.error("Error, no name found")
else:
	change_first_last_name(username, first_last_name)