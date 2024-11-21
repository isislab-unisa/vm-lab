import streamlit as st

from typing import Callable, List, Union, Literal
from streamlit_extras.card import card
from streamlit_extras.grid import grid
from backend.database import User, VirtualMachine
from backend.role import Role
from frontend.page_names import PageNames


def display_table_with_actions(
		data_list: list,
		data_type: Literal["user", "new_user", "vms"],
		details_callback: Callable[[Union[User, VirtualMachine]], None] = None,
		accept_new_user_callback: Callable[[User], None] = None,
		deny_new_user_callback: Callable[[User], None] = None,
		connect_callback: Callable[[VirtualMachine], None] = None,
):
	"""
	Display a table with dynamic behavior for Users or Virtual Machines.

	:param connect_callback:
	:param data_type:
	:param data_list: The list of Users or Virtual Machines to display.
	:param details_callback: Callback for "Details" button.
	:param accept_new_user_callback: Callback for "Accept" button (only for users).
	:param deny_new_user_callback: Callback for "Deny" button (only for users).
	"""
	if not data_list:
		st.write("No data to display.")
		return

	is_user_list = False
	is_new_user_list = False

	match data_type:
		case "user":
			header_fields = ['ID', 'Username', 'Email', 'First Name', 'Last Name', 'VM Count', 'Role']
			columns_width = (1, 2, 2, 2, 2, 1, 1, 1)  # Two extra columns for two buttons
			is_user_list = True
		case "new_user":
			header_fields = ['ID', 'Username', 'Email', 'First Name', 'Last Name']
			columns_width = (1, 2, 2, 2, 2, 1, 1)  # Two extra columns for two buttons
			is_user_list = True
			is_new_user_list = True
		case "vms":
			header_fields = ['ID', 'Name', 'Host', 'Username', 'Auth']
			columns_width = (1, 2, 2, 2, 1, 1, 1)  # Two extra columns for two buttons
		case _:
			raise ValueError("data_type must be 'user', 'new_user' or 'vms'")

	with st.container():
		# HEADER
		header_cols = st.columns(columns_width)
		for header_column, header_field in zip(header_cols, header_fields):
			header_column.write(f'**{header_field}**')

		# ROWS
		for item in data_list:
			row_column = st.columns(columns_width)

			if is_user_list:
				item: User = item
				row_column[0].write(item.id)
				row_column[1].write(item.username)
				row_column[2].write(item.email)
				row_column[3].write(item.first_name)
				row_column[4].write(item.last_name)

				if is_new_user_list:
					# New User data
					accept_column = row_column[5]
					deny_column = row_column[6]

					if accept_column.button(label="Accept", type="primary", key=f'{item.id}-accept'):
						if accept_new_user_callback:
							accept_new_user_callback(item)

					if deny_column.button(label="Deny", type="secondary", key=f'{item.id}-deny'):
						if deny_new_user_callback:
							deny_new_user_callback(item)
				else:
					# User data
					row_column[5].write(len(item.virtual_machines))
					row_column[6].write(item.role)
					details_column = row_column[7]

					if details_column.button(label="Details", type="primary", key=f'{item.id}-action'):
						if details_callback:
							details_callback(item)
			else:
				# Virtual Machine data
				item: VirtualMachine = item
				row_column[0].write(item.id)
				row_column[1].write(item.name)
				row_column[2].write(item.host)
				row_column[3].write(item.username)

				if item.ssh_key:
					row_column[4].write("`SSH Key`")
				elif item.password:
					row_column[4].write("`Password`")
				else:
					row_column[4].write("`None`")

				details_column = row_column[5]
				connect_column = row_column[6]

				if details_column.button(label="Details", type="secondary", key=f'{item.id}-action'):
					if details_callback:
						details_callback(item)

				if connect_column.button(label="Connect", type="primary", key=f'{item.id}-connect'):
					if connect_callback:
						connect_callback(item)


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
	"""Renders a grid with a list of Virtual Machine cards"""
	grids = grid(3)

	for vm in vm_list:
		with grids.empty():
			card(
				key=f"card-{vm.id}",
				title=vm.name,
				text=f"({vm.id}) {vm.host}:{vm.port}",
				on_click=lambda: on_click(vm)
			)
