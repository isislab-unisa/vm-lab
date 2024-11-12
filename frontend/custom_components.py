from typing import Callable, Literal, List

import streamlit as st
from streamlit_extras.card import card
from streamlit_extras.grid import grid

from backend.database import User, VirtualMachine
from backend.role import Role
from frontend.page_names import PageNames


def user_table_with_actions(user_list: list[User],
							details_callback: Callable[[User], None] = None,
							accept_callback: Callable[[User], None] = None,
							deny_callback: Callable[[User], None] = None,
							is_new_users_table: bool = False):
	"""
	Custom user table with a callable action button
	:param deny_callback: Callback function for when the deny button is clicked (when is_new_users_table=True)
	:param accept_callback: Callback function for when the accept button is clicked (when is_new_users_table=True)
	:param details_callback: Callback function for when the details button is clicked (when is_new_users_table=False)
	:param user_list: The list of users
	:param is_new_users_table: Whether to display 'VM Count' and 'Role' (False) or not (True)
	:return:
	"""
	if is_new_users_table:
		header_fields = ['ID', 'Username', 'Email', 'First Name', 'Last Name']
		columns_width = (1, 2, 2, 2, 2, 1, 1)
	else:
		header_fields = ['ID', 'Username', 'Email', 'First Name', 'Last Name', 'VM Count', 'Role']
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
				accept_column = cols[5]
				deny_column = cols[6]

				if accept_column.button(label="Accept", type="primary", key=f'{user.id}-accept'):
					accept_callback(user)

				if deny_column.button(label="Deny", type="secondary", key=f'{user.id}-deny'):
					deny_callback(user)

			else:
				cols[5].markdown(len(user.virtual_machines))
				cols[6].write(user.role)
				action_column = cols[7]

				if action_column.button(label="Details", type="primary", key=f'{user.id}-action'):
					details_callback(user)




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


def vm_cards_grid(vm_list: List[VirtualMachine], on_click: Callable[[VirtualMachine], None]):
	grids = grid(3)

	for vm in vm_list:
		with grids.empty():
			card(
				key=f"card-{vm.id}",
				title=vm.name,
				text=f"({vm.id}) {vm.ip}",
				on_click=lambda: on_click(vm)
			)