import streamlit as st
from streamlit import switch_page

from backend import Role
from backend.database import get_db
from backend.models import User

from frontend import PageNames, page_setup
from frontend.click_handlers.user import user_details_clicked
from frontend.components import interactive_data_table
from utils.session_state import get_session_state_item, pop_session_state_item

################################
#            SETUP             #
################################

psd = page_setup(
	title=PageNames.MANAGE_USER_LIST.label,
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.MAIN_DASHBOARD(),
)

current_username = psd.user_name
if current_username is None:
	switch_page(PageNames.ERROR())


if get_session_state_item("user_has_been_disabled"):
	st.cache_data.clear()
	pop_session_state_item("user_has_been_disabled")


################################
#     REFRESH DB FUNCTIONS     #
################################

@st.cache_data
def get_user_data_from_db():
	with get_db() as db:
		user_list = User.find_all(
			db=db,
			exclude_user_name=current_username,
			exclude_user_roles=[Role.ADMIN, Role.NEW_USER]
		)

	result = []
	for user in user_list:
		user_dict = {
			# Hidden
			"original_object": user,
			# Shown in columns
			"username": user.username,
			"first_name": user.first_name,
			"last_name": user.last_name,
			"email": user.email,
			"role": user.role,
			"disabled": ":heavy_check_mark: Yes" if user.disabled else ":x: No",
			# Button disabled settings
			"buttons_disabled": {}
		}
		result.append(user_dict)

	return result


################################
#             PAGE             #
################################

st.title(PageNames.MANAGE_USER_LIST.label)

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
		},
		"Is Disabled": {
			"column_width": 1,
			"data_name": "disabled"
		}
	},
	button_settings={
		"View": {
			"primary": True,
			"callback": user_details_clicked,
			"icon": ":material/arrow_forward:",
		},
	},
	action_header_name=None,
	filters_expanded=True
)