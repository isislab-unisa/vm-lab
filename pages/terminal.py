import streamlit as st
import streamlit.components.v1 as stv1

from streamlit import switch_page

from backend import Role

from frontend import PageNames, page_setup

from utils.session_state import get_session_state_item


################################
#            SETUP             #
################################

page_setup(
	title=PageNames.VM_CONNECTION.label,
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.SIDEKICK],
)

selected_vm = get_session_state_item("selected_vm")
ssh_url = get_session_state_item("terminal_page_ssh_connection_url")
sftp_url = get_session_state_item("terminal_page_sftp_connection_url")

if selected_vm is None or ssh_url is None or sftp_url is None:
	switch_page(PageNames.MAIN_DASHBOARD())

################################
#             PAGE             #
################################

st.title(f"{PageNames.VM_CONNECTION.label} `{selected_vm.name}`")

stv1.iframe(ssh_url, width=800, height=700)
stv1.iframe(sftp_url, width=800, height=700)