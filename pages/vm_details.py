import streamlit as st

from streamlit import switch_page

from backend.role import Role
from backend.database import get_db
from backend.models import VirtualMachine, User
from frontend.page_names import PageNames
from frontend.page_setup import page_setup
from frontend.custom_forms.vm import edit_vm_form, delete_vm_form, edit_vm_password_form, delete_vm_password_form, edit_vm_ssh_key_form, delete_ssh_key_form
from utils.session_state import get_session_state_item

psd = page_setup(
	title="Edit VM",
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.SIDEKICK],
)

selected_vm: VirtualMachine = get_session_state_item("selected_vm")
current_username: str = psd.user_name

if selected_vm is None or current_username is None:
	switch_page(PageNames.MAIN_DASHBOARD)

st.header(f"Edit VM `{selected_vm.name}`")

with get_db() as db:
	user = psd.get_user(db)

	edit_vm_form(selected_vm)

	edit_vm_password_form(selected_vm, user)

	if selected_vm.password:
		delete_vm_password_form(selected_vm)

	edit_vm_ssh_key_form(selected_vm, user)

	if selected_vm.ssh_key:
		delete_ssh_key_form(selected_vm)

	delete_vm_form(selected_vm)

