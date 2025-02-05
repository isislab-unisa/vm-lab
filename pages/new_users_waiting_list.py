import streamlit as st

from streamlit import switch_page

from backend import Role
from backend.models import User
from backend.database import get_db

from frontend import PageNames, page_setup
from frontend.click_handlers.manage_waiting_list import new_user_accept_clicked_as_manager, new_user_denied_clicked, \
	new_user_accept_clicked_as_admin
from frontend.components import interactive_data_table


################################
#            SETUP             #
################################

psd = page_setup(
	title=PageNames.MANAGE_WAITING_LIST.label,
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.MAIN_DASHBOARD(),
)

current_username = psd.user_name
current_role = psd.user_role

if current_username is None or current_role is None:
	switch_page(PageNames.ERROR())


################################
#     REFRESH DB FUNCTIONS     #
################################

@st.cache_data
def get_user_data_from_db():
	with get_db() as db:
		user_list = User.find_by_role(db, Role.NEW_USER)

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
			# Button disabled settings
			"buttons_disabled": {}
		}
		result.append(user_dict)

	return result


################################
#             PAGE             #
################################

st.header(PageNames.MANAGE_WAITING_LIST.label)

if current_role == Role.ADMIN:
	accept_callback = new_user_accept_clicked_as_admin
else:
	accept_callback = new_user_accept_clicked_as_manager

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
		"Accept": {
			"primary": True,
			"callback": accept_callback,
			"icon": ":material/check:",
		},
		"Deny": {
			"primary": False,
			"callback": new_user_denied_clicked,
			"icon": ":material/close:"
		}
	},
	action_header_name=None,
	popover_settings={
		"text": "Action"
	},
	filters_expanded=True
)


