import streamlit as st

from streamlit import switch_page
from typing import List, cast

from backend.role import Role
from backend.models import User
from backend.database import get_db
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from frontend.custom_components import display_table_with_actions
from utils.session_state import get_session_state_item, set_session_state_item

page_setup(
	title="Manage Users",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
)


def get_valid_users(avoid_username: str) -> List[User]:
	"""Not valid users are: Admins, New Users and the User requesting this function."""
	with get_db() as db:
		fetched_users = db.query(User) \
			.filter(User.role != Role.ADMIN.value) \
			.filter(User.role != Role.NEW_USER.value) \
			.filter(User.username != avoid_username) \
			.all()

		return cast(List[User], fetched_users)


def go_to_user_details(callback_user: User):
	set_session_state_item("selected_user", callback_user)
	switch_page(PageNames.user_details)


current_username = get_session_state_item("username")
if current_username is None:
	switch_page(PageNames.error)

users = get_valid_users(current_username)

st.title("Manage Users")
display_table_with_actions(
	data_type="user",
	data_list=users,
	details_callback=go_to_user_details
)
