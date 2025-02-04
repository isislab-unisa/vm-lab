import streamlit as st

from frontend.page_options import page_setup

psd = page_setup(
    title="Logout",
    access_control="logged_in_only",
)

st.cache_data.clear()  # Clear cache to refresh table data
psd.authenticator.logout(location="unrendered")
