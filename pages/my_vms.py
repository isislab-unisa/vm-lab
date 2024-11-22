import streamlit as st
from streamlit import switch_page
from backend.database import VirtualMachine, get_user_virtual_machines, get_db, User, get_user_bookmarks, Bookmark
from backend.role import Role
from frontend.custom_components import vm_cards_grid, display_table_with_actions
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state, set_session_state
from utils.terminal_connection import test_connection

page_setup(
	title="My VMs",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
)


@st.dialog("Add Virtual Machine")
def add_vm():
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
def add_bookmark():
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
	elif selected_vm.password:
		try:
			with st.spinner(text="Connecting..."):
				response_json = test_connection(
					hostname=selected_vm.host,
					port=selected_vm.port,
					username=selected_vm.username,
					password=selected_vm.decrypt_password()
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


@st.dialog("Edit VM")
def vm_details_clicked(selected_vm: VirtualMachine):
	with st.form(f"edit-form-vm-{selected_vm.id}"):
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

	st.divider()
	delete_button = st.button("Delete")

	if delete_button:
		with get_db() as db:
			try:
				vm_to_delete = db.query(VirtualMachine).filter(VirtualMachine.id == selected_vm.id).first()
				db.delete(vm_to_delete)
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Deleted")
				switch_page(PageNames.my_vms)


@st.dialog("Edit Bookmark")
def bookmark_details_clicked(selected_bookmark: Bookmark):
	with st.form(f"edit-form-bookmark-{selected_bookmark.id}"):
		name = st.text_input("VM name", value=selected_bookmark.name, placeholder="Insert name")
		link = st.text_input("Link", value=selected_bookmark.link, placeholder="Insert link")
		submit_button = st.form_submit_button("Edit", type="primary")

	if submit_button:
		with get_db() as db:
			try:
				bookmark = db.query(Bookmark).filter(Bookmark.id == selected_bookmark.id).first()
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
				bookmark_to_delete = db.query(Bookmark).filter(Bookmark.id == selected_bookmark.id).first()
				db.delete(bookmark_to_delete)
				db.commit()
			except Exception as e:
				st.error(f"An error has occurred: **{e}**")
			else:
				st.success(f"Deleted")
				switch_page(PageNames.my_vms)


st.title("My VMs")
current_username = get_session_state("username")

if current_username is None:
	switch_page(PageNames.error)

st.button("Add VM", on_click=add_vm)

vm_list = get_user_virtual_machines(current_username)

display_table_with_actions(
	data_type="vms",
	data_list=vm_list,
	details_callback=vm_details_clicked,
	connect_callback=connect_clicked,
)

st.divider()
st.title("My Bookmarks")

st.button("Add Bookmark", on_click=add_bookmark)

bookmark_list = get_user_bookmarks(current_username)

display_table_with_actions(
	data_type="bookmark",
	data_list=bookmark_list,
	details_callback=bookmark_details_clicked
)
