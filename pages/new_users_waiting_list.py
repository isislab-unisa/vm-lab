from typing import List, cast

import streamlit as st
from streamlit import switch_page

from backend.authentication import edit_user_in_authenticator_object, remove_user_in_authenticator_object
from backend.database import get_db, User
from backend.role import Role
from frontend.custom_components import display_table_with_actions
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType


def get_users() -> List[User]:
	with get_db() as db:
		fetched_users = db.query(User) \
			.filter(User.role == Role.NEW_USER.value) \
			.all()

		return cast(List[User], fetched_users)


page_setup(
	title="New Users",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
)

st.header("New Users Waiting List")

users = get_users()

@st.dialog("Select role")
def accept_clicked(callback_user: User):
	selection = st.selectbox(
		"Role",
		[Role.to_phrase(Role.USER), Role.to_phrase(Role.MANAGER)],
	)

	button = st.button("Add", type="primary")
	if button:
		selected_role = Role.from_phrase(selection).value
		with get_db() as db:
			user = db.query(User).filter(User.id == callback_user.id).first()
			user.role = selected_role
			db.commit()
			db.refresh(user)
			edit_user_in_authenticator_object(user.username, user)
			print("Accepted", callback_user.id)
			switch_page(PageNames.waiting_list)


@st.dialog("Are you sure?")
def denied_clicked(callback_user: User):
	col1, col2 = st.columns(2)

	with col1:
		yes_button = st.button("Yes")

		if yes_button:
			with get_db() as db:
				user = db.query(User).filter(User.id == callback_user.id).first()
				db.delete(user)
				db.commit()
				remove_user_in_authenticator_object(user.username)
				print("Denied", callback_user.id)
				switch_page(PageNames.waiting_list)

	with col2:
		no_button = st.button("No", type="primary")

		if no_button:
			st.rerun()



display_table_with_actions(
	data_type="new_user",
	data_list=users,
	accept_new_user_callback=accept_clicked,
	deny_new_user_callback=denied_clicked
)