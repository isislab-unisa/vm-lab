import streamlit as st

from frontend.page_options import page_setup

page_setup(
	title="Error",
	access_control="free_access",
)

st.title("Error")