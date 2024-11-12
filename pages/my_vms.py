import streamlit as st
from streamlit import switch_page
from backend.database import VirtualMachine, get_user_virtual_machines
from backend.role import Role
from frontend.custom_components import vm_cards_grid
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state, set_session_state
from utils.terminal_connection import test_connection, CREDENTIAL_KEYS

page_setup(
	title="My VMs",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
	print_session_state=True
)

st.title("My VMs")
current_username = get_session_state("username")

if current_username is None:
	switch_page(PageNames.error)


@st.dialog("Insert credentials")
def card_clicked(selected_vm: VirtualMachine):
	with st.form(f"connection-form-{selected_vm.id}"):
		st.write(f"Enter your credentials for {selected_vm.name}")
		host = st.text_input("Host", disabled=True, placeholder="Insert IP address or domain",
							 value=selected_vm.ip)
		port = st.number_input("Port", value=22)
		username = st.text_input("Username", placeholder="Insert username")
		password = st.text_input("Password", type="password", placeholder="Insert password")
		submit_button = st.form_submit_button("Connect")

	if submit_button:
		if not host or not username or not password:
			st.warning("Fill out all of the required fields.")
		else:
			try:
				test_connection(host, port, username, password)
				set_session_state("selected_vm", selected_vm)
				switch_page(PageNames.terminal)
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")


vm_list = get_user_virtual_machines(get_session_state("username"))
vm_cards_grid(vm_list, on_click=card_clicked)