import streamlit as st

from frontend import page_setup, PageNames

################################
#            SETUP             #
################################

page_setup(
	title=PageNames.ERROR.label,
	access_control="free_access",
)


################################
#             PAGE             #
################################

st.title("Error")