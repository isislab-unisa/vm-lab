import streamlit as st
from streamlit import switch_page
from backend.database import VirtualMachine, get_user_virtual_machines, get_db, User
from backend.role import Role
from frontend.custom_components import vm_cards_grid
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state, set_session_state
from utils.terminal_connection import test_connection

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


@st.dialog("Connect")
def card_clicked(selected_vm: VirtualMachine):
	if selected_vm.ssh_key:
		try:
			with st.spinner(text="Connecting..."):
				response_json = test_connection(
					hostname=selected_vm.host,
					port=selected_vm.port,
					username=selected_vm.username,
					ssh_key=selected_vm.decrypt_key()
				)

			if "url" in response_json:
				st.success(f"Success")
				set_session_state("selected_vm", selected_vm)
				set_session_state("terminal_url", response_json["url"])
				switch_page(PageNames.terminal)
			elif "error" in response_json:
				st.error(f"An error has occurred: **{response_json["error"]}**")

		except Exception as e:
			st.error(f"An error has occurred: **{e}**")
	else:
		with st.form(f"connection-form-{selected_vm.id}"):
			st.write(f"Enter your password for {selected_vm.name}")
			password = st.text_input("Password", type="password", placeholder="Insert password")
			submit_button = st.form_submit_button("Connect")

		if submit_button:
			if not password:
				st.warning("Type the password")
			else:
				try:
					with st.spinner(text="Connecting..."):
						response_json = test_connection(
							hostname=selected_vm.host,
							port=selected_vm.port,
							username=selected_vm.username,
							password=password
						)

					if "url" in response_json:
						st.success(f"Success")
						set_session_state("selected_vm", selected_vm)
						set_session_state("terminal_url", response_json["url"])
						switch_page(PageNames.terminal)
					elif "error" in response_json:
						st.error(f"An error has occurred: **{response_json["error"]}**")
				except Exception as e:
					st.error(f"An error has occurred: **{e}**")


@st.dialog("Insert details")
def add_vm():
	with st.form(f"add-vm-form"):
		name = st.text_input("VM name", placeholder="Insert name")
		host = st.text_input("Host", placeholder="Insert IP address or domain")
		port = st.number_input("Port", value=22)
		username = st.text_input("Username", placeholder="Insert SSH username")
		ssh_key = st.file_uploader("SSH Key")
		submit_button = st.form_submit_button("Save")

	if submit_button:
		if not name or not host or not port or not username:
			st.warning("Fill out all of the required fields.")
		else:
			try:
				with get_db() as db:
					new_vm = VirtualMachine(
						name=name,
						host=host,
						port=port,
						username=username,
					)
					user = db.query(User).filter(User.username == current_username).first()
					new_vm.user_id = user.id

					if ssh_key:
						new_vm.ssh_key = VirtualMachine.encrypt_key(ssh_key.getvalue())

					db.add(new_vm)
					db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Created")


button = st.button("Add VM", on_click=add_vm)

vm_list = get_user_virtual_machines(current_username)
vm_cards_grid(vm_list, on_click=card_clicked)
