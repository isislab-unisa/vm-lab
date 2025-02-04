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
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.SIDEKICK],
)

selected_vm = get_session_state_item("selected_vm")
ssh_url = get_session_state_item("terminal_page_ssh_connection_url")
sftp_url = get_session_state_item("terminal_page_sftp_connection_url")

if selected_vm is None or ssh_url is None or sftp_url is None:
	switch_page(PageNames.my_vms)

st.title(f"`{selected_vm.name}` SSH Terminal")

stv1.iframe(ssh_url, width=800, height=700)
stv1.iframe(sftp_url, width=800, height=700)