import streamlit as st
from streamlit import switch_page

from backend.database import get_db, add_to_db
from backend.models import VirtualMachine, User
from frontend.components.confirm import confirm_dialog
from frontend.page_names import PageNames
from utils.session_state import set_session_state_item, pop_session_state_item


################################
#     ADD, EDIT, DELETE VM     #
################################

def add_vm_form(current_username: str):
	"""Dialog to add a new Virtual Machine."""
	with st.form(f"add-vm-form", border=False):
		name = st.text_input("VM name", placeholder="Insert name")
		host = st.text_input("Host", placeholder="Insert IP address or domain")
		port = st.number_input("Port", value=22, placeholder="Insert port")
		username = st.text_input("Username", placeholder="Insert SSH username")
		shared = st.toggle("This Virtual Machine can be accessed by managers or admins of the system", value=True)
		password = st.text_input("Password (optional)", type="password", placeholder="Insert password (optional)")
		ssh_key = st.file_uploader("SSH Key (optional)")
		st.divider()
		submit_button = st.form_submit_button("Save", use_container_width=True)

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
						shared=shared,
					)
					user = User.find_by_user_name(db, current_username)

					if user is None:
						raise Exception("User not found")

					new_vm.user_id = user.id

					if password:
						new_vm.password = VirtualMachine.encrypt_password(password)

					if ssh_key:
						new_vm.ssh_key = VirtualMachine.encrypt_key(ssh_key.getvalue())

					add_to_db(db, new_vm)
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Created")
				st.cache_data.clear()  # Refresh my_vms table
				st.rerun()


def edit_vm_form(selected_vm: VirtualMachine, clear_on_submit: bool = False,
				 key: str = 'Edit VM information'):
	with st.form(key=key, clear_on_submit=clear_on_submit):
		st.subheader('Edit VM information')
		name = st.text_input("VM name", value=selected_vm.name, placeholder="Insert name")
		host = st.text_input("Host", value=selected_vm.host, placeholder="Insert IP address or domain")
		port = st.number_input("Port", value=selected_vm.port, placeholder="Insert port")
		username = st.text_input("Username", value=selected_vm.username, placeholder="Insert SSH username")
		shared = st.toggle("This Virtual Machine can be accessed by managers or admins of the system", value=selected_vm.shared)
		edit_submit_button = st.form_submit_button("Edit", type="primary")

	if edit_submit_button:
		with get_db() as db:
			try:
				vm = VirtualMachine.find_by_id(db, selected_vm.id)
				if vm is None:
					raise Exception("VM not found")

				vm.name = name
				vm.host = host
				vm.port = port
				vm.username = username
				vm.shared = shared
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Edited")
				switch_page(PageNames.MAIN_DASHBOARD)


def delete_vm_form(selected_vm: VirtualMachine, key: str = 'Delete VM'):
	def delete():
		with get_db() as db:
			try:
				vm_to_delete = VirtualMachine.find_by_id(db, selected_vm.id)

				if vm_to_delete is None:
					raise Exception("VM not found")

				db.delete(vm_to_delete)
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Deleted")
				pop_session_state_item("selected_vm")
				switch_page(PageNames.MAIN_DASHBOARD)


	with st.form(key=key):
		st.subheader('Delete VM')
		submit = st.form_submit_button("Delete", type="primary")

		if submit:
			confirm_dialog(text="Are you sure you want to delete the VM?", confirm_button_callback=delete)


################################
#  ADD, EDIT, DELETE PASSWORD  #
################################

def edit_vm_password_form(selected_vm: VirtualMachine, user: User, key='Change VM password'):
	@st.dialog("VM Password")
	def password_dialog(is_new: bool = False):
		with st.form("change-password-form", clear_on_submit=True, border=False):
			if is_new:
				password = st.text_input("New password", type="password")
			else:
				password = st.text_input("Current password", type="password", value=selected_vm.decrypt_password())
			submit = st.form_submit_button("Update password")

		if submit:
			if not password:
				st.error("Insert a non empty password")
			else:
				with get_db() as db:
					try:
						vm = VirtualMachine.find_by_id(db, selected_vm.id)
						if vm is None:
							raise Exception("VM not found")

						vm.password = VirtualMachine.encrypt_password(password)
						db.commit()
						db.refresh(vm)
						set_session_state_item("selected_vm", vm)
					except Exception as e:
						st.error(f"An error has occurred: **{e}**")
					else:
						st.success(f"Edited")
						switch_page(PageNames.DETAILS_VM)

	with st.form(key=key, clear_on_submit=True):
		if not selected_vm.password:
			st.subheader('No password set')
			user_password = st.text_input("Your account's password", type="password",
										  placeholder="Insert your account password")
			if st.form_submit_button("Set a password", type="primary"):
				if user.verify_password(user_password):
					password_dialog(True)
				else:
					st.error("The inserted password does not match with your password")
		else:
			st.subheader('Password authentication present')
			user_password = st.text_input("Your account's password", type="password",
										  placeholder="Insert your account password")
			if st.form_submit_button("See or update the password", type="primary"):
				if user.verify_password(user_password):
					password_dialog()
				else:
					st.error("The inserted password does not match with your password")


def delete_vm_password_form(selected_vm: VirtualMachine, key: str = 'Delete VM password'):
	def delete():
		with get_db() as db:
			try:
				vm = VirtualMachine.find_by_id(db, selected_vm.id)
				if vm is None:
					raise Exception("VM not found")

				vm.password = None
				db.commit()
				db.refresh(vm)
				set_session_state_item("selected_vm", vm)
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Edited")
				switch_page(PageNames.DETAILS_VM)

	with st.form(key=key):
		st.subheader("Remove Password")
		submit = st.form_submit_button("Remove", type="primary")

		if submit:
			confirm_dialog(text="Are you sure you want to remove the password?", confirm_button_callback=delete)


################################
#    ADD, EDIT, DELETE KEY     #
################################

def edit_vm_ssh_key_form(selected_vm: VirtualMachine, user: User, key='Change VM ssh key'):
	@st.dialog("VM SSH Key")
	def ssh_key_dialog(is_new: bool = False):
		with st.form("change-ssh-key-form", clear_on_submit=True, border=False):
			if not is_new:
				st.code(selected_vm.decrypt_key().decode("utf-8"))

			ssh_key = st.file_uploader("New SSH Key")
			submit = st.form_submit_button("Update SSH Key")

		if submit:
			if not ssh_key:
				st.error("Insert a new key")
			else:
				with get_db() as db:
					try:
						vm = VirtualMachine.find_by_id(db, selected_vm.id)
						if vm is None:
							raise Exception("VM not found")

						vm.ssh_key = VirtualMachine.encrypt_key(ssh_key.getvalue())
						db.commit()
						db.refresh(vm)
						set_session_state_item("selected_vm", vm)
					except Exception as e:
						st.error(f"An error has occurred: **{e}**")
					else:
						st.success(f"Edited")
						switch_page(PageNames.DETAILS_VM)

	with st.form(key=key, clear_on_submit=True):
		if not selected_vm.ssh_key:
			st.subheader('No SSH Key set')
			user_password = st.text_input("Your account's password", type="password",
										  placeholder="Insert your account password")
			if st.form_submit_button("Set an SSH Key", type="primary"):
				if user.verify_password(user_password):
					ssh_key_dialog(True)
				else:
					st.error("The inserted password does not match with your password")
		else:
			st.subheader('SSH Key authentication present')
			user_password = st.text_input("Your account's password", type="password",
										  placeholder="Insert your account password")
			if st.form_submit_button("See or update the key", type="primary"):
				if user.verify_password(user_password):
					ssh_key_dialog()
				else:
					st.error("The inserted password does not match with your password")


def delete_ssh_key_form(selected_vm: VirtualMachine, key: str = 'Delete VM SSH Key'):
	def delete():
		with get_db() as db:
			try:
				vm = VirtualMachine.find_by_id(db, selected_vm.id)
				if vm is None:
					raise Exception("VM not found")

				vm.ssh_key = None
				db.commit()
				db.refresh(vm)
				set_session_state_item("selected_vm", vm)
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Edited")
				switch_page(PageNames.DETAILS_VM)

	with st.form(key=key):
		st.subheader("Remove SSH Key")
		submit = st.form_submit_button("Remove", type="primary")

		if submit:
			confirm_dialog(text="Are you sure you want to remove the SSH Key?", confirm_button_callback=delete)
