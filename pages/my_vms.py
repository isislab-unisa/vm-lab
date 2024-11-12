import streamlit as st
from streamlit import switch_page

from backend.database import VirtualMachine, get_user_virtual_machines
from backend.role import Role
from frontend.custom_components import vm_cards_grid
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state, set_session_state

authenticator = page_setup(
	title="My VMs",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
	print_session_state=True
)

st.title("My VMs")
username = get_session_state("username")

if username is None:
	switch_page(PageNames.error)

vm_list = get_user_virtual_machines(username)

def card_clicked(selected_vm: VirtualMachine):
	set_session_state("selected_vm", selected_vm)
	switch_page(PageNames.terminal)

vm_cards_grid(vm_list, on_click=card_clicked)