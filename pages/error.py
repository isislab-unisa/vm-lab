import streamlit as st

from frontend.page_options import page_setup, AccessControlType

authenticator = page_setup(
	title="Error",
	access_control=AccessControlType.FREE_ACCESS,
	print_session_state=True
)

st.title("Error")