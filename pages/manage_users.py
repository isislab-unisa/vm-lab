from typing import List, cast

import streamlit as st
from streamlit import switch_page

from backend.authentication import get_current_user_role
from backend.database import get_db, User
from backend.role import Role
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state

def get_users() -> tuple[List[User], List[User]]:
	with get_db() as db:
		fetched_users = db.query(User) \
			.filter(User.role != Role.NEW_USER.value) \
			.all()

		fetched_new_users = db.query(User) \
			.filter(User.role == Role.NEW_USER.value) \
			.all()

		return cast(List[User], fetched_users), cast(List[User], fetched_new_users)

authenticator = page_setup(
	title="Manage Users",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
	print_session_state=False
)

st.title("Manage Users")

current_role = get_current_user_role()
current_username = get_session_state("username")

if current_role is None or current_username is None:
	switch_page(PageNames.error)

users, new_users = get_users()

st.subheader("Users")
user_data = []
for user in users:
	user_data.append({
		"ID": user.id,
		"Username": f'{user.username} (you)' if user.username == current_username else user.username,
		"Email": user.email,
		"First Name": user.first_name,
		"Last Name": user.last_name,
		"Role": user.role
	})

st.table(user_data)

st.subheader("New Users")
new_user_data = []
for new_user in new_users:
	new_user_data.append({
		"ID": new_user.id,
		"Username": new_user.username,
		"Email": new_user.email,
		"First Name": new_user.first_name,
		"Last Name": new_user.last_name,
	})

st.table(new_user_data)