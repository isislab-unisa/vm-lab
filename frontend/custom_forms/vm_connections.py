import time

import requests
import streamlit as st
from paramiko.ssh_exception import AuthenticationException
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine, User, Bookmark
from frontend.custom_components import confirm_dialog
from frontend.page_names import PageNames
from utils.session_state import set_session_state_item
from utils.terminal_connection import send_credentials_to_external_module, build_module_url, test_connection_with_paramiko


@st.dialog("Add Virtual Machine")
def vm_add_clicked(current_username: str):
	"""Dialog to add a new Virtual Machine."""
	with st.form(f"add-vm-form"):
		name = st.text_input("VM name", placeholder="Insert name")
		host = st.text_input("Host", placeholder="Insert IP address or domain")
		port = st.number_input("Port", value=22, placeholder="Insert port")
		username = st.text_input("Username", placeholder="Insert SSH username")
		password = st.text_input("Password (optional)", type="password", placeholder="Insert password (optional)")
		ssh_key = st.file_uploader("SSH Key (optional)")
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

					if password:
						new_vm.password = VirtualMachine.encrypt_password(password)

					if ssh_key:
						new_vm.ssh_key = VirtualMachine.encrypt_key(ssh_key.getvalue())

					db.add(new_vm)
					db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Created")
				st.cache_data.clear()  # Refresh my_vms table
				switch_page(PageNames.my_vms)


@st.dialog("Connect to VM")
def vm_connect_clicked(data_row):
	"""Dialog to handle the connection to a Virtual Machine."""
	selected_vm: VirtualMachine = data_row["original_object"]


	def was_request_successful(req) -> bool:
		"""Verifies if a request to a module was successful."""
		return "success" in req and req["success"]


	def handle_connection(
			hostname, port, username,
			password=None, ssh_key=None):
		"""Handles the connection logic and updates session state."""
		with st.status(f"Connecting to `{username}@{hostname}:{port}`", expanded=True) as connection_status:
			# Test the connection to the remote
			st.write("Connecting to remote server...")
			try:
				test_connection_with_paramiko(
					hostname=hostname,
					port=port,
					username=username,
					password=password,
					ssh_key=ssh_key
				)
			except AuthenticationException:
				connection_status.update(label="Error!", state="error", expanded=True)
				st.error("**An error has occurred while connecting to the remote server:** Authentication failed.")
				return
			except TimeoutError:
				connection_status.update(label="Error!", state="error", expanded=True)
				st.error("**An error has occurred while connecting to the remote server:** Could not connect to the remote server.")
				return
			except Exception as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				st.success(type(e))
				st.exception(e)
				return

			st.caption("Success!")
			# Send the credentials to the SSH module
			st.write("Requesting SSH terminal...")
			try:
				response_ssh = send_credentials_to_external_module(
					module_type="ssh",
					hostname=hostname,
					port=port,
					username=username,
					password=password,
					ssh_key=ssh_key
				)

				if not was_request_successful(response_ssh):
					connection_status.update(label="Error!", state="error", expanded=True)
					st.error(f"**An error has occurred while requesting the SSH terminal:** {response_ssh['error']}")
					return
			except requests.exceptions.ConnectionError as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				st.error(f"**An error has occurred while requesting the SSH terminal:** Could not reach SSH module.")
				return
			except Exception as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				st.exception(e)
				return

			st.caption("Success!")
			# Send the credentials to the SFTP module
			st.write("Requesting SFTP file explorer...")
			try:
				response_sftp = send_credentials_to_external_module(
					module_type="sftp",
					hostname=hostname,
					port=port,
					username=username,
					password=password,
					ssh_key=ssh_key
				)

				if not was_request_successful(response_sftp):
					connection_status.update(label="Error!", state="error", expanded=True)
					st.error(
						f"**An error has occurred while requesting the SFTP file explorer:** {response_sftp['error']}")
					return
			except requests.exceptions.ConnectionError as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				st.error(f"**An error has occurred while requesting the SFTP file explorer:** Could not reach SFTP module.")
				return
			except Exception as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				st.exception(e)
				return

			st.caption("Success!")
			connection_status.update(label="Connection successful! Redirecting to page...", state="complete", expanded=True)
			time.sleep(1)

			set_session_state_item("selected_vm", selected_vm)

			ssh_connection_url = build_module_url(
				connection_type="ssh",
				request_type="connection",
				connection_id=response_ssh["connection_uuid"]
			)
			set_session_state_item(
				"terminal_page_ssh_connection_url",
				ssh_connection_url
			)

			sftp_connection_url = build_module_url(
				connection_type="sftp",
				request_type="connection",
				connection_id=response_sftp["connection_uuid"]
			)
			set_session_state_item(
				"terminal_page_sftp_connection_url",
				sftp_connection_url
			)

			st.cache_data.clear()  # Refresh my_vms table
			switch_page(PageNames.terminal)


	if selected_vm.ssh_key:
		# Connect using SSH key
		handle_connection(
			hostname=selected_vm.host,
			port=selected_vm.port,
			username=selected_vm.username,
			ssh_key=selected_vm.decrypt_key()
		)
	elif selected_vm.password:
		# Connect using saved password
		handle_connection(
			hostname=selected_vm.host,
			port=selected_vm.port,
			username=selected_vm.username,
			password=selected_vm.decrypt_password()
		)
	else:
		# Prompt user for password
		with st.form(f"connection-form-{selected_vm.id}"):
			st.write(f"Enter your password for {selected_vm.name}")
			password_input = st.text_input("Password", type="password", placeholder="Insert password")
			submit_button = st.form_submit_button("Connect")

		if submit_button:
			if not password_input:
				st.warning("Type the password.")
			else:
				# Connect using user-provided password
				handle_connection(
					hostname=selected_vm.host,
					port=selected_vm.port,
					username=selected_vm.username,
					password=password_input
				)


def vm_edit_clicked(data_row):
	"""Handle click of the edit button for a Virtual Machine."""
	selected_vm: VirtualMachine = data_row["original_object"]
	st.cache_data.clear()  # Refresh my_vms table
	set_session_state_item("selected_vm", selected_vm)
	switch_page(PageNames.vm_details)


def vm_delete_clicked(data_row):
	"""Handle click of the delete button for a Virtual Machine."""
	selected_vm: VirtualMachine = data_row["original_object"]

	def deletion_process():
		print("Deleting VM...")
		st.cache_data.clear() # Refresh my_vms table

	confirm_dialog(
		text=f"Are you sure you want to delete `{selected_vm.name}`?",
		confirm_button_callback=deletion_process
	)


@st.dialog("Edit Bookmark")
def bookmark_details_clicked(selected_bookmark: Bookmark):
	"""Dialog to edit a Bookmark."""
	with st.form(f"edit-form-bookmark-{selected_bookmark.id}"):
		name = st.text_input("VM name", value=selected_bookmark.name, placeholder="Insert name")
		link = st.text_input("Link", value=selected_bookmark.link, placeholder="Insert link")
		submit_button = st.form_submit_button("Edit", type="primary")

	if submit_button:
		with get_db() as db:
			try:
				bookmark = Bookmark.find_by(db, bookmark_id=selected_bookmark.id)
				bookmark.name = name
				bookmark.link = link
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Edited")
				switch_page(PageNames.my_vms)

	st.divider()
	delete_button = st.button("Delete")

	if delete_button:
		with get_db() as db:
			try:
				bookmark_to_delete = Bookmark.find_by(db, bookmark_id=selected_bookmark.id)
				db.delete(bookmark_to_delete)
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Deleted")
				switch_page(PageNames.my_vms)



@st.dialog("Add Bookmark")
def add_bookmark_clicked(current_username: str):
	"""Dialog to add a new Bookmark."""
	with st.form(f"add-bookmark-form"):
		name = st.text_input("Bookmark name", placeholder="Insert name")
		link = st.text_input("Link", placeholder="Insert link", help="Must start with `www.`")
		submit_button = st.form_submit_button("Save")

	if submit_button:
		if not name or not link:
			st.warning("Fill out all of the required fields.")
		elif not link.startswith("www."):
			st.error("Insert a valid link")
		else:
			try:
				with get_db() as db:
					new_link = Bookmark(
						name=name,
						link=link,
					)
					user = db.query(User).filter(User.username == current_username).first()
					new_link.user_id = user.id

					db.add(new_link)
					db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Created")
				switch_page(PageNames.my_vms)
