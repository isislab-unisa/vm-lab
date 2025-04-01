import streamlit as st
from streamlit import switch_page

from backend.role import Role, role_has_enough_priority

from frontend import PageNames, page_setup
from frontend.components import interactive_data_table
from frontend.click_handlers.vm import vm_connect_clicked, vm_add_clicked, vm_edit_clicked, vm_delete_clicked, \
	vm_assign_clicked
from frontend.click_handlers.bookmark import bookmark_add_clicked, bookmark_edit_clicked, bookmark_delete_clicked
from utils.refresh_db_functions import get_vm_data_from_db, get_bookmark_data_from_db

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
#             PAGE             #
################################

if current_role != Role.REGULAR:
	st.title(f":blue[:material/tv:] My VMs")
	st.button(
		"Add VM",
		type="primary",
		icon=":material/add:",
		on_click=lambda: vm_add_clicked(current_username)
	)

	interactive_data_table(
		key="data_table_this_user_vms",
		data=get_vm_data_from_db(current_username, "my_owned_vms"),
		refresh_data_callback=lambda: get_vm_data_from_db(current_username, "my_owned_vms"),
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

if current_role == Role.SIDEKICK or current_role == Role.REGULAR:
	st.title(f":green[:material/tv:] VMs Assigned to Me")
	interactive_data_table(
		key="data_table_assigned_vms_to_this_user",
		data=get_vm_data_from_db(current_username, "my_assigned_vms"),
		refresh_data_callback=lambda: get_vm_data_from_db(current_username, "my_assigned_vms"),
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
		},
		action_header_name=None,
		filters_expanded=False
	)

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
		data=get_bookmark_data_from_db(current_username),
		refresh_data_callback=lambda: get_bookmark_data_from_db(current_username),
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
	st.title(":green[:material/tv_signin:] Assigned VMs")
	st.button(
		"Assign a new VM",
		icon=":material/assignment_add:",
		type="primary",
		on_click=lambda: vm_assign_clicked(current_username)
	)

	interactive_data_table(
		key="data_table_all_assigned_vms",
		data=get_vm_data_from_db(current_username, "all_assigned_vms"),
		refresh_data_callback=lambda: get_vm_data_from_db(current_username, "all_assigned_vms"),
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
			"Assigned To": {
				"column_width": 1,
				"data_name": "assigned_to"
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

minimum_permissions = st.secrets["vm_sharing_minimum_permissions"]

try:
	minimum_role = Role.from_phrase(minimum_permissions)
except ValueError:
	minimum_role = None # "disabled" in secrets.toml

if minimum_role and role_has_enough_priority(current_role, minimum_role):
	st.divider()
	st.title(":red[:material/lan:] Other Users' VMs")
	interactive_data_table(
		key="data_table_all_users_vms",
		data=get_vm_data_from_db(current_username, "all_owned_vms"),
		refresh_data_callback=lambda: get_vm_data_from_db(current_username, "all_owned_vms"),
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
			"Assigned To": {
				"column_width": 1,
				"data_name": "assigned_to"
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