import streamlit as st

from streamlit import switch_page
from typing import List, cast

from backend.role import Role
from backend.models import User
from backend.database import get_db
from frontend.page_names import PageNames
from frontend.page_options import page_setup
from frontend.custom_components import display_table_with_actions, interactive_data_table
from utils.session_state import get_session_state_item, set_session_state_item

psd = page_setup(
	title="Manage Users",
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.MAIN_DASHBOARD,
)

current_username = psd.user_name

if current_username is None:
	switch_page(PageNames.ERROR)

def get_valid_users(avoid_username: str) -> List[User]:
	"""Not valid users are: Admins, New Users and the User requesting this function."""
	with get_db() as db:
		fetched_users = db.query(User) \
			.filter(User.role != Role.ADMIN.value) \
			.filter(User.role != Role.NEW_USER.value) \
			.filter(User.username != avoid_username) \
			.all()

		return cast(List[User], fetched_users)


@st.cache_data
def get_user_data_from_db():
	users = get_valid_users(current_username)
	result = []
	for user in users:
		user_dict = {
			"original_object": user,
			"username": user.username,
			"first_name": user.first_name,
			"last_name": user.last_name,
			"email": user.email,
			"role": user.role,
		}
		result.append(user_dict)

	return result


def go_to_user_details(data_row):
	callback_user: User = data_row["original_object"]
	set_session_state_item("selected_user", callback_user)
	switch_page(PageNames.DETAILS_USER)


st.title("Manage Users")

interactive_data_table(
	key="data_table_users",
	data=get_user_data_from_db(),
	refresh_data_callback=get_user_data_from_db,
	column_settings={
		"Username": {
			"column_width": 1,
			"data_name": "username"
		},
		"First Name": {
			"column_width": 1,
			"data_name": "first_name"
		},
		"Last Name": {
			"column_width": 1,
			"data_name": "last_name"
		},
		"Email": {
			"column_width": 1,
			"data_name": "email"
		},
		"Role": {
			"column_width": 1,
			"data_name": "role"
		}
	},
	button_settings={
		"View": {
			"primary": True,
			"callback": go_to_user_details,
			"icon": ":material/arrow_forward:",
		},
	},
	action_header_name=None,
	filters_expanded=True
)