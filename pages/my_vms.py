from typing import Literal

import streamlit as st
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine, Bookmark, User
from backend.role import Role
from frontend.components.interactive_data_table import interactive_data_table
from frontend.click_handlers.vm import vm_connect_clicked
from frontend.page_names import PageNames
from frontend.page_setup import page_setup


################################
#            SETUP             #
################################

psd = page_setup(
	title="My VMs",
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.SIDEKICK],
)

current_username = psd.user_name
current_role = psd.user_role

if current_username is None or current_role is None:
	switch_page(PageNames.ERROR)



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
	try:
		with get_db() as db:
			if scope == "this_user":
				vm_list = VirtualMachine.find_by_user_name(db, current_username)
			elif scope == "all_users":
				vm_list = VirtualMachine.find_all(db, shared=True, exclude_user_name=current_username)
			else:
				raise ValueError("Invalid scope. Use 'user' or 'all'.")

		result = []
		for vm in vm_list:
			result.append(build_vm_dict(vm))

		return result
	except Exception as e:
		st.error(f"An error has occurred: **{e}**")


def build_vm_dict(vm: VirtualMachine):
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
		"requesting_user": current_username,
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
			"original_object": bookmark,
			"name": bookmark.name,
			"url": bookmark.link,
			"buttons_disabled": {}
		}
		result.append(bookmark_dict)

	return result


################################
#   CLICK HANDLER FUNCTIONS    #
################################




st.title(":blue[:material/tv:] My VMs")
st.button("Add VM",
		  type="primary",
		  icon=":material/add:",
		  on_click=lambda: add_vm_dialog_form(current_username)
)

interactive_data_table(
	key="data_table_myvms",
	data=get_vm_data_from_db("user"),
	refresh_data_callback=lambda: get_vm_data_from_db("user"),
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

st.divider()
st.title(":orange[:material/bookmark:] My Bookmarks")

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

minimum_permissions = st.secrets["vm_sharing_minimum_permissions"]
show_users_vms = False

if minimum_permissions == "manager" and (current_role == Role.ADMIN or current_role == Role.MANAGER):
	show_users_vms = True
elif minimum_permissions == "admin" and (current_role == Role.ADMIN):
	show_users_vms = True


if show_users_vms:
	st.divider()
	st.title(":green[:material/tv_signin:] Other Users' VMs")

	st.button("Add and Assign a new VM", icon=":material/assignment_add:", type="primary", on_click=lambda: print("test"))

	interactive_data_table(
		key="data_table_usersvms",
		data=get_vm_data_from_db("all"),
		refresh_data_callback=lambda: get_vm_data_from_db("all"),
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