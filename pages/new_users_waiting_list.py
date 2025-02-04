import streamlit as st

from streamlit import switch_page

from backend.role import Role
from backend.models import User
from backend.database import get_db
from backend.authentication import edit_user_in_authenticator_object, remove_user_in_authenticator_object
from frontend.page_names import PageNames
from frontend.page_options import page_setup
from frontend.custom_components import display_table_with_actions

page_setup(
	title="New Users",
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
)


@st.dialog("Select role")
def accept_clicked(callback_user: User):
	selection = st.selectbox(
		"Role",
		[Role.to_phrase(Role.SIDEKICK), Role.to_phrase(Role.MANAGER)],
	)

	button = st.button("Add", type="primary")
	if button:
		selected_role = Role.from_phrase(selection).value
		with get_db() as db:
			user = User.find_by_id(db, callback_user.id)
			user.role = selected_role
			db.commit()
			db.refresh(user)
			edit_user_in_authenticator_object(user.username, user)
			print("Accepted", user.id)
			switch_page(PageNames.waiting_list)


@st.dialog("Are you sure?")
def denied_clicked(callback_user: User):
	col1, col2 = st.columns(2)

	with col1:
		yes_button = st.button("Yes")

		if yes_button:
			with get_db() as db:
				user = User.find_by_id(db, callback_user.id)
				db.delete(user)
				db.commit()

				remove_user_in_authenticator_object(callback_user.username)
				print("Denied", callback_user.id)
				switch_page(PageNames.waiting_list)

	with col2:
		no_button = st.button("No", type="primary")

		if no_button:
			st.rerun()


with get_db() as db_for_list:
	user_list = User.find_by_role(db_for_list, Role.NEW_USER)

st.header("New Users Waiting List")
display_table_with_actions(
	data_type="new_user",
	data_list=user_list,
	accept_new_user_callback=accept_clicked,
	deny_new_user_callback=denied_clicked
)
