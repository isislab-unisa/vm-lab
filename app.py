import streamlit as st
from streamlit import switch_page
from frontend.page_names import PageNames

switch_page(PageNames.MAIN_DASHBOARD())

# if st.button("Go to my vms", type="primary"):
# 	switch_page(PageNames.MAIN_DASHBOARD())