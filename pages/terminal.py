import streamlit as st
from streamlit import switch_page

from backend.role import Role
from frontend.custom_components import ssh_terminal
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state
from utils.terminal_connection import clear_connection_credentials, are_credentials_missing, get_connection_credentials

page_setup(
	title="Terminal",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
)

selected_vm = get_session_state("selected_vm")

if selected_vm is None or are_credentials_missing():
	clear_connection_credentials()
	switch_page(PageNames.my_vms)

st.title("Terminal")
st.write(selected_vm)

host, port, username, password = get_connection_credentials()

ssh_terminal(
	hostname=host,
	port=port,
	username=username,
	password=password
)
