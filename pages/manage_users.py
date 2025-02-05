import streamlit as st
from streamlit import switch_page

from backend.database import get_db
from backend.models import User
from backend.role import Role
from frontend.components.interactive_data_table import interactive_data_table
from frontend.page_names import PageNames
from frontend.page_setup import page_setup
from utils.session_state import set_session_state_item

################################
#            SETUP             #
################################

psd = page_setup(
	title="Manage Users",
	access_control="accepted_roles_only",
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.MAIN_DASHBOARD,
)

current_username = psd.user_name
if current_username is None:
	switch_page(PageNames.ERROR)


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
			"original_object": user,
			"username": user.username,
			"first_name": user.first_name,
			"last_name": user.last_name,
			"email": user.email,
			"role": user.role,
			"buttons_disabled": {}
		}
		result.append(user_dict)

	return result


################################
#   CLICK HANDLER FUNCTIONS    #
################################

def handle_user_details_click(data_row):
	callback_user: User = data_row["original_object"]
	set_session_state_item("selected_user", callback_user)
	switch_page(PageNames.DETAILS_USER)


################################
#             PAGE             #
################################

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
			"callback": handle_user_details_click,
			"icon": ":material/arrow_forward:",
		},
	},
	action_header_name=None,
	filters_expanded=True
)