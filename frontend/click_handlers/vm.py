import time

import requests
import streamlit as st
from paramiko import AuthenticationException
from streamlit import switch_page

from backend.database import get_db, delete_from_db
from backend.models import VirtualMachine
from exceptions import ModuleResponseError, VmNotSharedError
from frontend.components import confirm_dialog, error_toast, error_message
from frontend import PageNames
from frontend.forms.vm import add_vm_form, vm_delete_form
from utils.session_state import set_session_state_item
from utils.terminal_connection import test_connection_with_paramiko, send_credentials_to_external_module, \
	build_module_url


@st.dialog("Add new VM")
def vm_add_clicked(current_username: str):
	return add_vm_form(current_username)


def vm_edit_clicked(data_row):
	selected_vm: VirtualMachine = data_row["original_object"]
	st.cache_data.clear()  # Refresh my_vms table
	set_session_state_item("selected_vm", selected_vm)
	switch_page(PageNames.DETAILS_VM())


def vm_delete_clicked(data_row):
	selected_vm: VirtualMachine = data_row["original_object"]
	return vm_delete_form(selected_vm)


@st.dialog("Connecting to VM")
def vm_connect_clicked(data_row):
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
				error_message(
					when="while connecting to the remote server",
					cause="Authentication failed."
				)
				return
			except TimeoutError:
				connection_status.update(label="Error!", state="error", expanded=True)
				error_message(
					when="while connecting to the remote server",
					cause="Could not connect to the remote server."
				)
				return
			except Exception as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				error_message(
					unknown_exception=e,
					when="while connecting to the remote server",
				)
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
					raise ModuleResponseError(
						module_name="SSH",
						message=response_ssh['error']
					)
			except requests.exceptions.ConnectionError as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				error_message(
					when="while requesting the SSH terminal",
					cause="Could not reach SSH module."
				)
				return
			except ModuleResponseError as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				error_message(
					when="while requesting the SSH terminal",
					cause=str(e)
				)
				return
			except Exception as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				error_message(
					unknown_exception=e,
					when="while requesting the SSH terminal",
				)
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
					raise ModuleResponseError(
						module_name="SFTP",
						message=response_sftp['error']
					)
			except requests.exceptions.ConnectionError as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				error_message(
					when="while requesting the SFTP file explorer",
					cause="Could not reach SFTP module."
				)
				return
			except ModuleResponseError as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				error_message(
					when="while requesting the SFTP file explorer",
					cause=str(e)
				)
			except Exception as e:
				connection_status.update(label="Error!", state="error", expanded=True)
				error_message(
					unknown_exception=e,
					when="while requesting the SFTP file explorer",
				)
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
			switch_page(PageNames.VM_CONNECTION())

	try:
		selected_vm: VirtualMachine = data_row["original_object"]
		vm_shared = selected_vm.shared
		vm_owner: str = data_row["owner"]
		requesting_user: str = data_row["requesting_user"]

		if vm_owner != requesting_user and not vm_shared:
			raise VmNotSharedError(selected_vm.name)

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
	except VmNotSharedError as e:
		error_message(cause=str(e))
	except Exception as e:
		error_message(unknown_exception=e)
