import streamlit as st
from streamlit import switch_page

from backend.role import Role
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state

page_setup(
	title="Terminal",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
	print_session_state=True
)

selected_vm = get_session_state("selected_vm")
if selected_vm is None:
	switch_page(PageNames.my_vms)

st.title("Terminal")
st.write(selected_vm)