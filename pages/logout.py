import streamlit as st

from frontend import page_setup, PageNames

################################
#            SETUP             #
################################

psd = page_setup(
    title=PageNames.LOGOUT.label,
    access_control="logged_in_only",
)


################################
#             PAGE             #
################################

st.cache_data.clear()  # Clear cache to refresh table data
psd.authenticator.logout(location="unrendered")
