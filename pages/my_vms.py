import streamlit as st
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine, Bookmark
from backend.role import Role
from frontend.custom_components import interactive_data_table, confirm_dialog
from frontend.custom_forms.vm_connections import vm_add_clicked, vm_connect_clicked, vm_delete_clicked, vm_edit_clicked
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state_item

page_setup(
	title="My VMs",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
)

st.title("My VMs")
current_username = get_session_state_item("username")

if current_username is None:
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
			"host_complete": f":red[{vm.host}] : :blue[{vm.port}]",
			"username": vm.username,
			"auth": auth_type,
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
		vm_dict = {
			"name": bookmark.name,
			"url": bookmark.link,
		}
		result.append(vm_dict)

	return result


st.button("Add VM", on_click=lambda: vm_add_clicked(current_username))

interactive_data_table(
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
	filters_expanded=True
)

#display_table_with_actions(
#	data_type="vms",
#	data_list=vm_list,
#	details_callback=vm_details_clicked,
#	connect_callback=connect_clicked,
#)
#
#st.divider()
#st.title("My Bookmarks")
#
#st.button("Add Bookmark", on_click=lambda: add_bookmark(current_username))
#display_table_with_actions(
#	data_type="bookmark",
#	data_list=bookmark_list,
#	details_callback=bookmark_details_clicked
#)
