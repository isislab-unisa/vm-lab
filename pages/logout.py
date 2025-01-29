import streamlit as st

from frontend.page_options import page_setup, AccessControlType

authenticator = page_setup(
    title="Logout",
    access_control=AccessControlType.LOGGED_IN_ONLY,
)

st.cache_data.clear() # Clear cache to refresh table data
authenticator.logout(location="unrendered")
