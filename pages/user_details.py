import streamlit as st
from streamlit import switch_page

from backend.authentication import get_current_user_role, edit_user_in_authenticator_object
from backend.database import User, get_db, VirtualMachine, get_user_virtual_machines
from backend.role import Role
from frontend.custom_components import vm_cards_grid
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state, pop_session_state, set_session_state

page_setup(
	title="User Details",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
	print_session_state=False
)

selected_user: User = get_session_state("selected_user")
curren_role: Role = get_current_user_role()

if selected_user is None or curren_role is None:
	switch_page(PageNames.manage_users)

st.header(f"Details of `{selected_user.username}`")

st.write(f"ID: {selected_user.id}")
st.write(f"Email: {selected_user.email}")
st.write(f"First Name: {selected_user.first_name}")
st.write(f"Last Name: {selected_user.last_name}")



# The segmented_controls widget can be only found in streamlit 1.40.0, so a radio button is used for the 1.39.0 version
# https://docs.streamlit.io/develop/api-reference/widgets/st.segmented_control
# TODO: Update streamlit
if curren_role == Role.ADMIN:
	selection = st.radio(
		"Role",
		[Role.to_phrase(Role.USER), Role.to_phrase(Role.MANAGER)],
		index=0 if selected_user.role == Role.USER.value else 1
	)

	if Role.from_phrase(selection).value == selected_user.role:
		button = st.button("Change Role", type="primary", disabled=True)
	else:
		button = st.button("Change Role", type="primary")

	if get_session_state("role-change-success"):
		pop_session_state("role-change-success")
		st.success("Role changed successfully")

	if button:
		print("Change Role")
		with get_db() as db:
			user = db.query(User).filter(User.id == selected_user.id).first()
			user.role = Role.from_phrase(selection).value
			db.commit()
			db.refresh(user)
			set_session_state("selected_user", user)
			set_session_state("role-change-success", True)
			edit_user_in_authenticator_object(user.username, user)
			switch_page(PageNames.user_details)
else:
	st.write(f"Role: {Role.to_phrase(Role.from_str(selected_user.role))}")

st.divider()
st.subheader("Virtual Machines")

vm_list = get_user_virtual_machines(selected_user.username)

def card_clicked(selected_vm: VirtualMachine):
	set_session_state("selected_vm", selected_vm)
	switch_page(PageNames.terminal)

vm_cards_grid(vm_list, on_click=card_clicked)
