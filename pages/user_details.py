import streamlit as st

from streamlit import switch_page

from backend.role import Role
from backend.database import get_db
from backend.models import User, VirtualMachine
from backend.authentication import get_current_user_role, edit_user_in_authenticator_object
from frontend.custom_forms.vm_connections import vm_connect_clicked
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from frontend.custom_components import display_table_with_actions
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
		[Role.to_phrase(Role.USER), Role.to_phrase(Role.MANAGER)],
		index=0 if selected_user.role == Role.USER.value else 1
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
			user = User.find_by(db, user_id=selected_user.id)
			user.role = Role.from_phrase(selection).value
			db.commit()
			db.refresh(user)
			set_session_state_item("selected_user", user)
			set_session_state_item("role-change-success", True)
			edit_user_in_authenticator_object(user.username, user)
			switch_page(PageNames.user_details)
else:
	st.write(f"Role: {Role.to_phrase(Role.from_string(selected_user.role))}")

st.divider()
st.subheader("Virtual Machines")

with get_db() as db_list:
	vm_list = VirtualMachine.find_by(db_list, user_name=selected_user.username)

display_table_with_actions(
	data_type="vms",
	data_list=vm_list,
	connect_callback=vm_connect_clicked
)
