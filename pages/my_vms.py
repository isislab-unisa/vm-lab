import streamlit as st
from streamlit import switch_page

from backend.authentication import get_current_user_role
from backend.database import get_db
from backend.models import VirtualMachine, Bookmark, User
from backend.role import Role
from frontend.custom_components import interactive_data_table, confirm_dialog
from frontend.custom_forms.vm_connections import vm_add_clicked, vm_connect_clicked, vm_delete_clicked, vm_edit_clicked, \
	bookmark_add_clicked, bookmark_delete_clicked, bookmark_edit_clicked
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state_item

page_setup(
	title="My VMs",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
)


current_username = get_session_state_item("username")
current_role = get_current_user_role()

if current_username is None or current_role is None:
	switch_page(PageNames.error)


@st.cache_data
def get_vm_data_from_db():
	with get_db() as db_vm_list:
		print("Accessing db for vms...")
		vm_list = VirtualMachine.find_by(db_vm_list, user_name=current_username)

	result = []
	for vm in vm_list:
		if vm.ssh_key:
			auth_type = "`SSH Key`"
		elif vm.password:
			auth_type = "`Password`"
		else:
			auth_type = "`None`"

		vm_dict = {
			"original_object": vm, # Hidden object from the db ready to use
			"name": vm.name,
			"host_complete": f":blue[{vm.host}] : :red[{vm.port}]",
			"username": vm.username,
			"auth": auth_type,
			"buttons_disabled": {

			}
		}
		result.append(vm_dict)

	return result


@st.cache_data
def get_vm_data_from_db_for_all_users():
	with get_db() as db_vm_list:
		print("Accessing db for vms...")
		current_user_id = User.find_by(db_vm_list, user_name=current_username).id
		all_vms = VirtualMachine.find_all(db_vm_list)
		vm_list = []
		for vm in all_vms:
			if vm.user_id != current_user_id:
				vm_list.append(vm)

	result = []
	for vm in vm_list:
		if vm.ssh_key:
			auth_type = "`SSH Key`"
		elif vm.password:
			auth_type = "`Password`"
		else:
			auth_type = "`None`"

		vm_dict = {
			"original_object": vm, # Hidden object from the db ready to use
			"name": vm.name,
			"host_complete": f":blue[{vm.host}] : :red[{vm.port}]",
			"username": vm.username,
			"auth": auth_type,
			"owner": vm.user.__dict__["username"],
			"buttons_disabled": {

			}

		}
		result.append(vm_dict)

	return result

@st.cache_data
def get_bookmark_data_from_db():
	with get_db() as db_bookmark_list:
		print("Accessing db for bookmarks...")
		bookmark_list = Bookmark.find_by(db_bookmark_list, user_name=current_username)

	result = []
	for bookmark in bookmark_list:
		bookmark_dict = {
			"original_object": bookmark,
			"name": bookmark.name,
			"url": bookmark.link,
		}
		result.append(bookmark_dict)

	return result

st.title("My VMs")
st.button("Add VM", type="primary", icon=":material/add:", on_click=lambda: vm_add_clicked(current_username))

interactive_data_table(
	key="data_table_myvms",
	data=get_vm_data_from_db(),
	refresh_data_callback=get_vm_data_from_db,
	column_settings={
		"Name": {
			"column_width": 1,
			"data_name": "name"
		},
		"Host": {
			"column_width": 1,
			"data_name": "host_complete"
		},
		"Username": {
			"column_width": 1,
			"data_name": "username"
		},
		"Auth": {
			"column_width": 1,
			"data_name": "auth"
		},
	},
	button_settings={
		"Connect": {
			"primary": True,
			"callback": vm_connect_clicked,
			"icon": ":material/arrow_forward:",
		},
		"Edit": {
			"primary": False,
			"callback": vm_edit_clicked,
			"icon": ":material/edit:",
		},
		"Delete": {
			"primary": False,
			"callback": vm_delete_clicked,
			"icon": ":material/delete:",
		}
	},
	action_header_name=None,
	popover_settings={
		"text": "View"
	},
	filters_expanded=False
)

st.divider()
st.title("My Bookmarks")

st.button("Add Bookmark", type="primary", icon=":material/add:", on_click=lambda: bookmark_add_clicked(current_username))

interactive_data_table(
	key="data_table_mybookmarks",
	data=get_bookmark_data_from_db(),
	refresh_data_callback=get_bookmark_data_from_db,
	column_settings={
		"Name": {
			"column_width": 1,
			"data_name": "name"
		},
		"URL": {
			"column_width": 3,
			"data_name": "url"
		},
	},
	button_settings={
		"Edit": {
			"primary": False,
			"callback": bookmark_edit_clicked,
			"icon": ":material/edit:",
		},
		"Delete": {
			"primary": False,
			"callback": bookmark_delete_clicked,
			"icon": ":material/delete:",
		}
	},
	action_header_name=None,
	popover_settings={
		"text": "View"
	},
	filters_expanded=False
)

if current_role == Role.ADMIN or current_role == Role.MANAGER:
	st.divider()
	st.title("Other Users' VMs")

	st.button("Create and Assign a new VM", icon=":material/assignment_add:", type="primary", on_click=lambda: print("test"))

	interactive_data_table(
		key="data_table_usersvms",
		data=get_vm_data_from_db_for_all_users(),
		refresh_data_callback=get_vm_data_from_db_for_all_users,
		column_settings={
			"Name": {
				"column_width": 1,
				"data_name": "name"
			},
			"Owner": {
				"column_width": 1,
				"data_name": "owner"
			},
			"Host": {
				"column_width": 1,
				"data_name": "host_complete"
			},
			"Username": {
				"column_width": 1,
				"data_name": "username"
			},
			"Auth": {
				"column_width": 1,
				"data_name": "auth"
			},
		},
		button_settings={
			"Connect": {
				"primary": True,
				"callback": vm_connect_clicked,
				"icon": ":material/arrow_forward:",
			},
			"Edit": {
				"primary": False,
				"callback": vm_edit_clicked,
				"icon": ":material/edit:",
			},
			"Delete": {
				"primary": False,
				"callback": vm_delete_clicked,
				"icon": ":material/delete:",
			}
		},
		action_header_name=None,
		popover_settings={
			"text": "View"
		},
		filters_expanded=False
	)