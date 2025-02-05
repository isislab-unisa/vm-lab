import streamlit as st

from frontend.page_setup import page_setup

################################
#            SETUP             #
################################

page_setup(
	title="Error",
	access_control="free_access",
)


################################
#             PAGE             #
################################

st.title("Error")