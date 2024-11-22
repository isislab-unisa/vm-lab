from time import sleep
from typing import Callable

import streamlit as st

from streamlit import switch_page
from backend.database import VirtualMachine, get_db, User
from frontend.page_names import PageNames
from utils.session_state import set_session_state


@st.dialog("Are you sure?")
def confirm_dialog(confirm_callback: Callable = None, *args, **kwargs):
	col1, col2 = st.columns(2)

	with col1:
		yes_button = st.button("Yes", type="primary")

		if yes_button and confirm_callback:
			confirm_callback(*args, **kwargs)

	with col2:
		no_button = st.button("No")

		if no_button:
			st.rerun()


def confirm_toggle(confirm_callback: Callable = None, *args, **kwargs):
	on = st.toggle("Are you sure?")
	button = st.button("Confirm")

	if button and on and confirm_callback:
		confirm_callback(*args, **kwargs)

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
						vm = db.query(VirtualMachine).filter(VirtualMachine.id == selected_vm.id).first()
						vm.password = VirtualMachine.encrypt_password(password)
						db.commit()
						db.refresh(vm)
						set_session_state("selected_vm", vm)
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
				vm = db.query(VirtualMachine).filter(VirtualMachine.id == selected_vm.id).first()
				vm.password = None
				db.commit()
				db.refresh(vm)
				set_session_state("selected_vm", vm)
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Edited")
				switch_page(PageNames.vm_details)

	with st.form(key=key):
		st.subheader("Remove Password")
		submit = st.form_submit_button("Remove", type="primary")

		if submit:
			confirm_dialog(delete)



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
				vm = db.query(VirtualMachine).filter(VirtualMachine.id == selected_vm.id).first()
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
	def delete(vm_id):
		with get_db() as db:
			try:
				vm_to_delete = db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
				db.delete(vm_to_delete)
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Deleted")
				switch_page(PageNames.my_vms)


	with st.form(key=key):
		st.subheader('Delete VM')
		if st.form_submit_button("Delete", type="primary"):
			confirm_dialog(lambda: delete(selected_vm.id))



