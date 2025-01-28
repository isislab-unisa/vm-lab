import streamlit as st
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine
from frontend.custom_components import interactive_data_table
from frontend.page_names import PageNames

#switch_page(PageNames.my_vms)
if st.button("Go to my vms", type="primary"):
	switch_page(PageNames.my_vms)


e = RuntimeError("This is an exception of type RuntimeError")
st.exception(e)