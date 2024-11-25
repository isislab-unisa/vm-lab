import streamlit as st
import streamlit.components.v1 as stv1

from streamlit import switch_page

from backend.role import Role
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state_item

page_setup(
	title="Terminal",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
)

selected_vm = get_session_state_item("selected_vm")
terminal_url = get_session_state_item("terminal_url")

if selected_vm is None or terminal_url is None:
	switch_page(PageNames.my_vms)

st.title(f"`{selected_vm.name}` SSH Terminal")

stv1.iframe(terminal_url, width=800, height=800)