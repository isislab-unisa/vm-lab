import streamlit as st
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine, User, Bookmark
from frontend.page_names import PageNames
from utils.session_state import set_session_state_item
from utils.terminal_connection import test_connection


@st.dialog("Add Virtual Machine")
def add_vm(current_username):
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
				switch_page(PageNames.my_vms)


@st.dialog("Add Bookmark")
def add_bookmark(current_username):
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


@st.dialog("Connect")
def connect_clicked(selected_vm: VirtualMachine):
	"""Dialog to handle the connection to a Virtual Machine."""

	def handle_connection(hostname, port, username, password=None, ssh_key=None):
		"""Handles the connection logic and updates session state."""
		try:
			with st.spinner(text=f"Connecting with {'SSH Key' if ssh_key else 'Password'}..."):
				response_ssh, response_sftp = test_connection(
					hostname=hostname,
					port=port,
					username=username,
					password=password,
					ssh_key=ssh_key,
					terminal_url="http://192.168.1.101:8888",
					sftp_url="http://192.168.1.101:8261"
				)

			if "url" in response_ssh and "key" in response_sftp:
				st.success("Success")
				set_session_state_item("selected_vm", selected_vm)
				set_session_state_item(
					"terminal_url", f"http://192.168.1.101:8888/{response_ssh["create_session_id"]}"
				)
				set_session_state_item(
					"sftp_url", f"http://192.168.1.101:8261/?connection={response_sftp['key']}"
				)
				switch_page(PageNames.terminal)
			elif "error" in response_ssh:
				st.error(f"An error has occurred: **{response_ssh['error']}**")
			else:
				st.error("An error has occurred")

		except Exception as e:
			st.error(f"An error has occurred: **{e}**")

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
			password = st.text_input("Password", type="password", placeholder="Insert password")
			submit_button = st.form_submit_button("Connect")

		if submit_button:
			if not password:
				st.warning("Type the password")
			else:
				# Connect using user-provided password
				handle_connection(
					hostname=selected_vm.host,
					port=selected_vm.port,
					username=selected_vm.username,
					password=password
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


def vm_details_clicked(selected_vm: VirtualMachine):
	"""Handle click of detail button for a Virtual Machine."""
	set_session_state_item("selected_vm", selected_vm)
	switch_page(PageNames.vm_details)
