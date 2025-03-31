import streamlit as st
from typing import Literal
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine, Bookmark
from backend.role import Role, role_has_enough_priority

from frontend import PageNames, page_setup
from frontend.components import interactive_data_table, error_message
from frontend.click_handlers.vm import vm_connect_clicked, vm_add_clicked, vm_edit_clicked, vm_delete_clicked
from frontend.click_handlers.bookmark import bookmark_add_clicked, bookmark_edit_clicked, bookmark_delete_clicked

################################
#            SETUP             #
################################

psd = page_setup(
	title="My Dashboard",
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.SIDEKICK, Role.REGULAR],
)

current_username = psd.user_name
current_role = psd.user_role

if current_username is None or current_role is None:
	switch_page(PageNames.ERROR())


################################
#     REFRESH DB FUNCTIONS     #
################################

@st.cache_data
def get_vm_data_from_db(scope: Literal["this_user", "all_users"] = "user"):
	"""
	Fetch VM data from the database.

	:param scope: Whether to get the VMs for the current user ("this_user") or all users except for the current user ("all_users").
	:return: List of dictionaries with VM info.
	"""
	requesting_user_name = current_username

	try:
		with get_db() as db:
			if scope == "this_user":
				vm_list = VirtualMachine.find_by_user_name(db, requesting_user_name)
			elif scope == "all_users":
				vm_list = VirtualMachine.find_all(db, shared=True, exclude_user_name=requesting_user_name)
			else:
				raise ValueError("Invalid scope. Use 'user' or 'all'.")

		result = []
		for vm in vm_list:
			result.append(build_vm_dict(vm, requesting_user_name))

		return result
	except ValueError as e:
		error_message(cause=str(e))
	except Exception as e:
		error_message(unknown_exception=e)


def build_vm_dict(vm: VirtualMachine, requesting_user_name: str):
	"""Build a correct dictionary with the VM info to display in the table."""
	if vm.ssh_key:
		auth_type = ":material/key: SSH Key"
	elif vm.password:
		auth_type = ":material/password: Password"
	else:
		auth_type = ":material/do_not_disturb_on: None"

	try:
		owner = vm.user.username
	except KeyError:
		raise KeyError(f"Could not find the owner of the VM `{vm.name}`.")

	vm_dict = {
		# Hidden
		"original_object": vm,
		"requesting_user": requesting_user_name,
		# Shown in columns
		"name": vm.name,
		"host_complete": f":blue[{vm.host}] : :red[{vm.port}]",
		"username": vm.username,
		"shared": ":heavy_check_mark: Yes" if vm.shared else ":x: No",
		"auth": auth_type,
		"owner": owner,
		# Button disabled settings
		"buttons_disabled": {}
	}

	return vm_dict


@st.cache_data
def get_bookmark_data_from_db():
	with get_db() as db_bookmark_list:
		bookmark_list = Bookmark.find_by_user_name(db_bookmark_list, current_username)

	result = []
	for bookmark in bookmark_list:
		bookmark_dict = {
			# Hidden
			"original_object": bookmark,
			# Shown in columns
			"name": bookmark.name,
			"url": bookmark.link,
			# Button disabled settings
			"buttons_disabled": {}
		}
		result.append(bookmark_dict)

	return result


################################
#             PAGE             #
################################

my_vms_title = "My VMs"

if current_role == Role.REGULAR:
	my_vms_title = "VMs Assigned To Me"

st.title(f":blue[:material/tv:] {my_vms_title}")

if current_role != Role.REGULAR:
	st.button(
		"Add VM",
		type="primary",
		icon=":material/add:",
		on_click=lambda: vm_add_clicked(current_username)
	)

	interactive_data_table(
		key="data_table_this_user_vms",
		data=get_vm_data_from_db("this_user"),
		refresh_data_callback=lambda: get_vm_data_from_db("this_user"),
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
			"Is Shared": {
				"column_width": 1,
				"data_name": "shared"
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
else:
	pass


if current_role != Role.REGULAR:
	st.divider()
	st.title(":orange[:material/bookmark:] My Bookmarks")

	st.button(
		"Add Bookmark",
		type="primary",
		icon=":material/add:",
		on_click=lambda: bookmark_add_clicked(current_username)
	)

	interactive_data_table(
		key="data_table_bookmarks",
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

minimum_permissions = st.secrets["vm_sharing_minimum_permissions"]
if role_has_enough_priority(current_role, Role.from_phrase(minimum_permissions)):
	st.divider()
	st.title(":green[:material/tv_signin:] Other Users' VMs")

	st.button(
		"Assign a new VM",
		icon=":material/assignment_add:",
		type="primary",
		on_click=lambda: print("Yet to implement...")  # TODO: Implement this
	)

	interactive_data_table(
		key="data_table_all_users_vms",
		data=get_vm_data_from_db("all_users"),
		refresh_data_callback=lambda: get_vm_data_from_db("all_users"),
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
			"Is Shared": {
				"column_width": 1,
				"data_name": "shared"
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
