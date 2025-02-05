import streamlit as st

from streamlit import switch_page

from backend.role import Role
from backend.database import get_db
from backend.models import VirtualMachine
from frontend.page_names import PageNames
from frontend.page_setup import page_setup
from frontend.forms.vm import vm_edit_form, vm_delete_form, vm_password_edit_form, vm_password_delete_form, vm_ssh_key_edit_form, ssh_key_delete_form
from utils.session_state import get_session_state_item

psd = page_setup(
	title="Edit VM",
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.SIDEKICK],
)

selected_vm: VirtualMachine = get_session_state_item("selected_vm")
current_username: str = psd.user_name

if selected_vm is None or current_username is None:
	switch_page(PageNames.MAIN_DASHBOARD())

st.header(f"Edit VM `{selected_vm.name}`")

with get_db() as db:
	user = psd.get_user(db)

	vm_edit_form(selected_vm)

	vm_password_edit_form(selected_vm, user)

	if selected_vm.password:
		vm_password_delete_form(selected_vm)

	vm_ssh_key_edit_form(selected_vm, user)

	if selected_vm.ssh_key:
		ssh_key_delete_form(selected_vm)


	if st.button("Delete VM", type="primary"):
		vm_delete_form(selected_vm)

