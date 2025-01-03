import streamlit as st

from streamlit import switch_page

from backend.role import Role
from backend.database import get_db
from backend.models import VirtualMachine, Bookmark
from frontend.custom_forms.vm_connections import add_vm, add_bookmark, connect_clicked, bookmark_details_clicked, \
	vm_details_clicked
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from frontend.custom_components import display_table_with_actions
from utils.session_state import get_session_state_item

page_setup(
	title="My VMs",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
)

st.title("My VMs")
current_username = get_session_state_item("username")

if current_username is None:
	switch_page(PageNames.error)

with get_db() as db_list:
	vm_list = VirtualMachine.find_by(db_list, user_name=current_username)
	bookmark_list = Bookmark.find_by(db_list, user_name=current_username)

st.button("Add VM", on_click=lambda: add_vm(current_username))
display_table_with_actions(
	data_type="vms",
	data_list=vm_list,
	details_callback=vm_details_clicked,
	connect_callback=connect_clicked,
)

st.divider()
st.title("My Bookmarks")

st.button("Add Bookmark", on_click=lambda: add_bookmark(current_username))
display_table_with_actions(
	data_type="bookmark",
	data_list=bookmark_list,
	details_callback=bookmark_details_clicked
)
