import streamlit as st

from backend.database import User
from backend.role import Role
from frontend.page_names import PageNames


def user_table_with_actions(user_list: list[User], button_callback: callable, is_new_users_table: bool = False,
							button_label: str = "Action", button_type: str = "primary"):

	if is_new_users_table:
		header_fields = ['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Action']
		columns_width = (1, 2, 2, 2, 2, 1)
	else:
		header_fields = ['ID', 'Username', 'Email', 'First Name', 'Last Name', 'VM Count', 'Role', 'Action']
		columns_width = (1, 2, 2, 2, 2, 1, 1, 1)

	with st.container():
		# HEADER
		header_columns = st.columns(columns_width)
		for column, field in zip(header_columns, header_fields):
			column.write(f'**{field}**')

		# ROWS
		for user in user_list:
			if is_new_users_table:
				col1, col2, col3, col4, col5, col6 = st.columns(columns_width)
				col1.write(user.id)
				col2.write(user.username)
				col3.write(user.email)
				col4.write(user.first_name)
				col5.write(user.last_name)

				button_column = col6.empty()
				clicked = button_column.button(label=button_label, type=button_type, key=f'{user.id}-action')
				if clicked:
					button_callback(user)
			else:
				col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(columns_width)
				col1.write(user.id)
				col2.write(user.username)
				col3.write(user.email)
				col4.write(user.first_name)
				col5.write(user.last_name)
				col6.write(len(user.virtual_machines))
				col7.write(user.role)

				button_column = col8.empty()
				clicked = button_column.button(label=button_label, type=button_type, key=f'{user.id}-action')
				if clicked:
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
