from typing import List, cast

import streamlit as st
from streamlit import switch_page

from backend.database import get_db, User
from backend.role import Role
from frontend.custom_components import user_table_with_actions
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state


def get_users(avoid_username: str) -> List[User]:
	with get_db() as db:
		fetched_users = db.query(User) \
			.filter(User.role != Role.ADMIN.value) \
			.filter(User.role != Role.NEW_USER.value) \
			.filter(User.username != avoid_username) \
			.all()

		return cast(List[User], fetched_users)

page_setup(
	title="Manage Users",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
	print_session_state=False
)

st.title("Manage Users")

current_username = get_session_state("username")
if current_username is None:
	switch_page(PageNames.error)

users = get_users(current_username)

# df_users = pd.DataFrame(user_data)
#
# # Option 1: DATA EDITOR
# st.write("#### Option 1: DATA EDITOR")
# st.data_editor(
# 	df_users,
# 	column_config={
# 		"ID": st.column_config.NumberColumn(disabled=True),
# 		"Username": st.column_config.TextColumn(disabled=True),
# 		"Email": st.column_config.TextColumn(disabled=True),
# 		"First Name": st.column_config.TextColumn(disabled=True),
# 		"Last Name": st.column_config.TextColumn(disabled=True),
# 		"VM Count": st.column_config.NumberColumn(disabled=True),
# 		"Role": st.column_config.SelectboxColumn(
# 			options=[
# 				Role.MANAGER.value,
# 				Role.USER.value
# 			],
# 			required=True,
# 		),
# 	},
# 	hide_index=True
# )
#
#
# st.write("#### Option 2: TABLE")
# st.table(user_data)
#
#
# st.write("#### Option 3: DATA FRAME WITH SELECTION")
# # https://discuss.streamlit.io/t/button-inside-a-dataframe/69427/12
# event = st.dataframe(
# 	df_users,
# 	on_select="rerun",
# 	hide_index=True,
# 	selection_mode="single-row"
# )
#
# if len(event.selection['rows']):
# 	selected_row = event.selection['rows'][0]
# 	username = df_users.iloc[selected_row]['Username']
# 	email = df_users.iloc[selected_row]['Email']
#
# 	st.session_state['user_data'] = {'username': username, 'email': email}
# 	st.write(f"Goto {username}'s page")
#
#
# st.write("#### Option 4: CUSTOM TABLE")

def user_print(callback_user: User):
	print(callback_user.id)

user_table_with_actions(
	user_list=users,
	button_callback=user_print
)
