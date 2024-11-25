import streamlit as st

from frontend.page_options import page_setup, AccessControlType

page_setup(
	title="Error",
	access_control=AccessControlType.FREE_ACCESS,
)

st.title("Error")