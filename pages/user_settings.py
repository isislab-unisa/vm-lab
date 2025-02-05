import streamlit as st

from frontend import page_setup
from frontend.forms.user import change_username, change_email, change_password, change_first_last_name

psd = page_setup(
	title="User Settings",
	access_control="logged_in_only"
)

username = psd.user_name
email = psd.user_email
first_last_name = psd.user_full_name

st.title("User Settings")

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