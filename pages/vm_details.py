import streamlit as st

from streamlit import switch_page

from backend.role import Role
from backend.database import get_db
from backend.models import VirtualMachine, User
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from frontend.custom_forms.vm_details import edit_vm, delete_vm, edit_vm_password, delete_password, edit_vm_ssh_key, delete_ssh_key
from utils.session_state import get_session_state_item

page_setup(
	title="Edit VM",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
)

selected_vm: VirtualMachine = get_session_state_item("selected_vm")
current_username: str = get_session_state_item("username")

if selected_vm is None or current_username is None:
	switch_page(PageNames.my_vms)

st.header(f"Edit VM `{selected_vm.name}`")

with get_db() as db:
	user = User.find_by_user_name(db, current_username)

	edit_vm(selected_vm)

	edit_vm_password(selected_vm, user)

	if selected_vm.password:
		delete_password(selected_vm)

	edit_vm_ssh_key(selected_vm, user)

	if selected_vm.ssh_key:
		delete_ssh_key(selected_vm)

	delete_vm(selected_vm)

