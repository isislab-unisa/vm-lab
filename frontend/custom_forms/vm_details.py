import streamlit as st
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine, User
from frontend.custom_components import confirm_dialog
from frontend.page_names import PageNames
from utils.session_state import set_session_state_item, pop_session_state_item


def edit_vm_password(selected_vm: VirtualMachine, user: User, key='Change VM password'):
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
						switch_page(PageNames.vm_details)

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


def delete_password(selected_vm: VirtualMachine, key: str = 'Delete VM password'):
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
				switch_page(PageNames.vm_details)

	with st.form(key=key):
		st.subheader("Remove Password")
		submit = st.form_submit_button("Remove", type="primary")

		if submit:
			confirm_dialog(text="Are you sure you want to remove the password?", confirm_button_callback=delete)


def edit_vm_ssh_key(selected_vm: VirtualMachine, user: User, key='Change VM ssh key'):
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
						switch_page(PageNames.vm_details)

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


def delete_ssh_key(selected_vm: VirtualMachine, key: str = 'Delete VM SSH Key'):
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
				switch_page(PageNames.vm_details)

	with st.form(key=key):
		st.subheader("Remove SSH Key")
		submit = st.form_submit_button("Remove", type="primary")

		if submit:
			confirm_dialog(text="Are you sure you want to remove the SSH Key?", confirm_button_callback=delete)


def edit_vm(selected_vm: VirtualMachine, clear_on_submit: bool = False,
			key: str = 'Edit VM information'):
	with st.form(key=key, clear_on_submit=clear_on_submit):
		st.subheader('Edit VM information')
		name = st.text_input("VM name", value=selected_vm.name, placeholder="Insert name")
		host = st.text_input("Host", value=selected_vm.host, placeholder="Insert IP address or domain")
		port = st.number_input("Port", value=selected_vm.port, placeholder="Insert port")
		username = st.text_input("Username", value=selected_vm.username, placeholder="Insert SSH username")
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
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Edited")
				switch_page(PageNames.my_vms)


def delete_vm(selected_vm: VirtualMachine, key: str = 'Delete VM'):
	def delete():
		with get_db() as db:
			try:
				vm_to_delete = db.query(VirtualMachine).filter(VirtualMachine.id == selected_vm.id).first()
				db.delete(vm_to_delete)
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Deleted")
				pop_session_state_item("selected_vm")
				switch_page(PageNames.my_vms)


	with st.form(key=key):
		st.subheader('Delete VM')
		submit = st.form_submit_button("Delete", type="primary")

		if submit:
			confirm_dialog(text="Are you sure you want to delete the VM?", confirm_button_callback=delete)
