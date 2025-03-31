from typing import Literal

import streamlit as st
from streamlit import switch_page

from backend import Role, get_db
from backend.authentication.user_data_manipulation import disable_user, delete_user
from backend.models import User, VirtualMachine

from frontend import PageNames, page_setup
from frontend.click_handlers.vm import vm_connect_clicked, vm_edit_clicked, vm_delete_clicked
from frontend.components import error_message, confirm_dialog
from frontend.components.interactive_data_table import interactive_data_table
from frontend.forms.user import change_role_form
from utils.refresh_db_functions import get_vm_data_from_db

from utils.session_state import get_session_state_item, set_session_state_item

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

if selected_user is None or curren_role is None or get_session_state_item("user_has_been_disabled_or_enabled"):
	switch_page(PageNames.MANAGE_USER_LIST())


################################
#             PAGE             #
################################

if selected_user.disabled:
	st.header(f"Details of user `{selected_user.username}` (USER HAS BEEN DISABLED)")
else:
	st.header(f"Details of user `{selected_user.username}`")
st.write(f"ID: {selected_user.id}")
st.write(f"Email: {selected_user.email}")
st.write(f"First Name: {selected_user.first_name}")
st.write(f"Last Name: {selected_user.last_name}")


# Role select box
change_role_form(selected_user, curren_role)

def disable():
	disable_user(selected_user.username)
	set_session_state_item("user_has_been_disabled_or_enabled", True)

	# Force all vms to be shared
	with get_db() as db:
		vms = VirtualMachine.find_by_user_name(db, selected_user.username)
		for vm in vms:
			if not vm.shared:
				vm.shared = True
				db.commit()


def delete():
	delete_user(selected_user.username)
	set_session_state_item("user_has_been_disabled_or_enabled", True)


def revert():
	disable_user(selected_user.username, revert=True)
	set_session_state_item("user_has_been_disabled_or_enabled", True)


if not selected_user.disabled:
	st.button("Disable User", on_click=lambda: confirm_dialog(
		":warning: WARNING: Are you sure you want to disable this user?",
		"The user WILL NOT be deleted. All the user's VMs will become shared.",
		is_confirm_button_type_primary=True,
		confirm_button_callback=disable,
	))
else:
	st.button("Revert Disabling", on_click=lambda: confirm_dialog(
		"Are you sure you want to **REVERT THE DISABLING** of this user?",
		"All the user's VMs will still be shared.",
		is_confirm_button_type_primary=True,
		confirm_button_callback=revert,
	))

	st.button("Delete User", on_click=lambda: confirm_dialog(
		":warning: WARNING: Are you sure you want to **PERMANENTLY DELETE** this user?",
		"All the user's VMs will be DELETED.",
		is_confirm_button_type_primary=True,
		confirm_button_callback=delete,
	))


st.divider()
st.subheader("Virtual Machines")

# Reuse the functions from my_vms.py
interactive_data_table(
	key="data_table_this_user_vms",
	data=get_vm_data_from_db(selected_user.username, "owned_vms", True),
	refresh_data_callback=lambda: get_vm_data_from_db(selected_user.username, "owned_vms", True),
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