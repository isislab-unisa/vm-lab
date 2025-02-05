import streamlit as st

from frontend.page_setup import page_setup


################################
#            SETUP             #
################################

psd = page_setup(
    title="Logout",
    access_control="logged_in_only",
)


################################
#             PAGE             #
################################

st.cache_data.clear()  # Clear cache to refresh table data
psd.authenticator.logout(location="unrendered")
