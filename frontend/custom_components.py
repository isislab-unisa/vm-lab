from typing import Callable, Literal

import streamlit as st

from backend.database import User
from backend.role import Role
from frontend.page_names import PageNames


def user_table_with_actions(user_list: list[User], button_callback: Callable[[User], None],
							is_new_users_table: bool = False, button_label: str = "Action",
							button_type: Literal["primary", "secondary"] = "primary"):
	"""
	Custom user table with a callable action button
	:param user_list: The list of users
	:param button_callback: The callback function to be called when the action button is clicked
	:param is_new_users_table: Whether to display 'VM Count' and 'Role' (False) or not (True)
	:param button_label: The label of the button
	:param button_type: The type of the button
	:return:
	"""
	if is_new_users_table:
		header_fields = ['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Action']
		columns_width = (1, 2, 2, 2, 2, 1)
	else:
		header_fields = ['ID', 'Username', 'Email', 'First Name', 'Last Name', 'VM Count', 'Role', 'Action']
		columns_width = (1, 2, 2, 2, 2, 1, 1, 1)

	with st.container():
		# HEADER
		header_cols = st.columns(columns_width)
		for col, field in zip(header_cols, header_fields):
			col.write(f'**{field}**')

		# ROWS
		for user in user_list:
			cols = st.columns(columns_width)
			cols[0].write(user.id)
			cols[1].write(user.username)
			cols[2].write(user.email)
			cols[3].write(user.first_name)
			cols[4].write(user.last_name)

			if is_new_users_table:
				action_column = cols[5]
			else:
				cols[5].write(len(user.virtual_machines))
				cols[6].write(user.role)
				action_column = cols[7]

			if action_column.button(label=button_label, type=button_type, key=f'{user.id}-action'):
				button_callback(user)


def render_sidebar_menu(role: Role | None):
	"""
	Renders the sidebar menu based on the user's role stored in the session state
	https://docs.streamlit.io/develop/tutorials/multipage/st.page_link-nav
	"""
	with st.sidebar:
		match role:
			case Role.NEW_USER:
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.USER:
				st.page_link(PageNames.my_vms, label="My VMs")
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.MANAGER:
				st.page_link(PageNames.my_vms, label="My VMs")
				st.page_link(PageNames.manage_users, label="Manage Users")
				st.page_link(PageNames.waiting_list, label="New Users")
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.ADMIN:
				st.page_link(PageNames.my_vms, label="My VMs")
				st.page_link(PageNames.manage_users, label="Manage Users")
				st.page_link(PageNames.waiting_list, label="New Users")
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case _:  # Not logged in
				st.page_link(PageNames.login, label="Login")
				st.page_link(PageNames.register, label="Register")
				st.page_link(PageNames.forgot_credentials, label="Forgot Credentials")
