from typing import List, cast

import streamlit as st
from streamlit import switch_page

from backend.database import get_db, User
from backend.role import Role
from frontend.custom_components import display_table_with_actions
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType
from utils.session_state import get_session_state, set_session_state


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

# user_list = []
# for user in users:
# 	user_list.append({
# 		"ID": user.id,
# 		"Username": user.username,
# 		"Email": user.email,
# 		"First Name": user.first_name,
# 		"Last Name": user.last_name,
# 		"VM Count": len(user.virtual_machines),
# 		"Role": user.role
# 	})
#
# df_users = pd.DataFrame(user_list)
#
# # Option 1: DATA EDITOR
# st.write("#### Option 1: DATA EDITOR")
# # Showcase solution, database change not implemented
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
# st.write("#### Option 2: STATIC TABLE")
# st.table(user_list)
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
#
# 	if st.button(f"Go to {username}'s page"):
# 		with get_db() as db:
# 			# Showcase solution, avoid doing this
# 			user = db.query(User).filter(User.username == username).first()
# 			set_session_state("selected_user", user)
# 		switch_page(PageNames.user_details)
#
#
# st.write("#### Option 4: CUSTOM TABLE")

def go_to_user_details(callback_user: User):
	set_session_state("selected_user", callback_user)
	switch_page(PageNames.user_details)

display_table_with_actions(
	data_type="user",
	data_list=users,
	details_callback=go_to_user_details
)
