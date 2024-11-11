from typing import List, cast

import streamlit as st

from backend.database import get_db, User
from backend.role import Role
from frontend.custom_components import user_table_with_actions
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType


def get_users() -> List[User]:
	with get_db() as db:
		fetched_users = db.query(User) \
			.filter(User.role == Role.NEW_USER.value) \
			.all()

		return cast(List[User], fetched_users)


page_setup(
	title="Manage Users",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
	print_session_state=False
)

st.header("New Users Waiting List")

users = get_users()

def user_print(callback_user: User):
	print(callback_user.id)

user_table_with_actions(
	is_new_users_table=True,
	user_list=users,
	button_callback=user_print
)