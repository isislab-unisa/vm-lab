import streamlit as st

from streamlit import switch_page

from backend.role import Role
from backend.database import get_db
from backend.models import User, VirtualMachine
from backend.authentication import get_current_user_role, edit_user_in_authenticator_object
from frontend.custom_forms.vm_connections import vm_connect_clicked, vm_edit_clicked, vm_delete_clicked
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from frontend.custom_components import display_table_with_actions, interactive_data_table
from utils.session_state import get_session_state_item, pop_session_state_item, set_session_state_item
from utils.terminal_connection import send_credentials_to_external_module

page_setup(
	title="User Details",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
)


selected_user: User = get_session_state_item("selected_user")
curren_role: Role = get_current_user_role()

if selected_user is None or curren_role is None:
	switch_page(PageNames.manage_users)

st.header(f"Details of user `{selected_user.username}`")
st.write(f"ID: {selected_user.id}")
st.write(f"Email: {selected_user.email}")
st.write(f"First Name: {selected_user.first_name}")
st.write(f"Last Name: {selected_user.last_name}")

# Role select box
if curren_role == Role.ADMIN:
	selection = st.selectbox(
		"Role",
		[Role.to_phrase(Role.SIDEKICK), Role.to_phrase(Role.MANAGER)],
		index=0 if selected_user.role == Role.SIDEKICK.value else 1
	)

	if Role.from_phrase(selection).value == selected_user.role:
		button = st.button("Change Role", type="primary", disabled=True)
	else:
		button = st.button("Change Role", type="primary")

	if get_session_state_item("role-change-success"):
		pop_session_state_item("role-change-success")
		st.success("Role changed successfully")

	if button:
		print("Change Role")
		with get_db() as db:
			user = User.find_by_id(db, selected_user.id)
			user.role = Role.from_phrase(selection).value
			db.commit()
			db.refresh(user)
			set_session_state_item("selected_user", user)
			set_session_state_item("role-change-success", True)
			edit_user_in_authenticator_object(user.username, user)
			switch_page(PageNames.user_details)
else:
	st.write(f"Role: {Role.to_phrase(Role(selected_user.role))}")

st.divider()
st.subheader("Virtual Machines")


@st.cache_data
def get_user_vm_from_db():
	with get_db() as db_list:
		vm_list = VirtualMachine.find_by_user_name(db_list, selected_user.username)

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


interactive_data_table(
	key="data_table_myvms",
	data=get_user_vm_from_db(),
	refresh_data_callback=get_user_vm_from_db,
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