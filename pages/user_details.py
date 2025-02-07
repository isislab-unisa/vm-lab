from typing import Literal

import streamlit as st
from streamlit import switch_page

from backend import Role, get_db
from backend.models import User, VirtualMachine

from frontend import PageNames, page_setup
from frontend.click_handlers.vm import vm_connect_clicked, vm_edit_clicked, vm_delete_clicked
from frontend.components import error_message
from frontend.components.interactive_data_table import interactive_data_table
from frontend.forms.user import change_role_form

from utils.session_state import get_session_state_item


################################
#            SETUP             #
################################

psd = page_setup(
	title=PageNames.DETAILS_USER.label,
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.MAIN_DASHBOARD(),
)

curren_role = psd.user_role
selected_user: User = get_session_state_item("selected_user")

if selected_user is None or curren_role is None:
	switch_page(PageNames.MANAGE_USER_LIST())



@st.cache_data
def get_vm_data_from_db(scope: Literal["this_user", "all_users"] = "user"):
	"""
	Fetch VM data from the database.

	:param scope: Whether to get the VMs for the current user ("this_user") or all users except for the current user ("all_users").
	:return: List of dictionaries with VM info.
	"""
	requesting_user_name = selected_user.username

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


################################
#             PAGE             #
################################

st.header(f"Details of user `{selected_user.username}`")
st.write(f"ID: {selected_user.id}")
st.write(f"Email: {selected_user.email}")
st.write(f"First Name: {selected_user.first_name}")
st.write(f"Last Name: {selected_user.last_name}")

# Role select box
change_role_form(selected_user, curren_role)

st.divider()
st.subheader("Virtual Machines")

# Reuse the functions from my_vms.py
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