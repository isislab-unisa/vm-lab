import streamlit as st

from streamlit import switch_page
from backend.database import VirtualMachine, get_db, User
from backend.role import Role
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state
from frontend.custom_forms_vms import edit_vm, delete_vm, edit_vm_password, delete_password

page_setup(
	title="Edit VM",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
)

# st.divider()
# delete_button = st.button("Delete")
#
# if delete_button:
# 	with get_db() as db:
# 		try:
# 			vm_to_delete = db.query(VirtualMachine).filter(VirtualMachine.id == selected_vm.id).first()
# 			db.delete(vm_to_delete)
# 			db.commit()
# 		except Exception as e:
# 			st.error(f"An error has occurred: **{e}**")
# 		else:
# 			st.success(f"Deleted")
# 			switch_page(PageNames.my_vms)

selected_vm: VirtualMachine = get_session_state("selected_vm")
current_username: str = get_session_state("username")

if selected_vm is None or current_username is None:
	switch_page(PageNames.my_vms)

st.header(f"Edit VM `{selected_vm.name}`")

with get_db() as db:
	user = db.query(User).filter(User.username == current_username).first()
	edit_vm(selected_vm)
	edit_vm_password(selected_vm, user)
	if selected_vm.password:
		delete_password(selected_vm)
	delete_vm(selected_vm)

