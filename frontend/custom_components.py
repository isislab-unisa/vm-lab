import streamlit as st

from typing import Callable, Union, Literal

from plotly.validators.pointcloud.marker import border

from backend.models import User, VirtualMachine, Bookmark
from backend.role import Role
from frontend.page_names import PageNames


def display_table_with_actions(
		data_list: list,
		data_type: Literal["user", "new_user", "vms", "bookmark"],
		details_callback: Callable[[Union[User, VirtualMachine, Bookmark]], None] = None,
		accept_new_user_callback: Callable[[User], None] = None,
		deny_new_user_callback: Callable[[User], None] = None,
		connect_callback: Callable[[VirtualMachine], None] = None,
):
	"""
	Display a table with dynamic behavior for Users or Virtual Machines.

	:param data_list: The list of Users or Virtual Machines to display
	:param data_type: The type of data passed, can be: "user", "new_user", "vms" or "bookmark"
	:param details_callback: Callback for "Details" button
	:param accept_new_user_callback: Callback for "Accept" button (only for users)
	:param deny_new_user_callback: Callback for "Deny" button (only for users)
	:param connect_callback: Callback for "Connect" button (only for vms)
	"""
	if not data_list:
		st.write("No data to display.")
		return

	is_user_list = False
	is_new_user_list = False
	is_vm_list = False

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
			is_vm_list = True
		case "bookmark":
			header_fields = ['ID', 'Name', 'URL']
			columns_width = (1, 2, 2, 1)  # One extra column for one button
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

					if accept_column.button(label="Accept", type="primary", key=f'new-user-{item.id}-accept'):
						if accept_new_user_callback:
							accept_new_user_callback(item)

					if deny_column.button(label="Deny", type="secondary", key=f'new-user-{item.id}-deny'):
						if deny_new_user_callback:
							deny_new_user_callback(item)
				else:
					# User data
					row_column[5].write(len(item.virtual_machines))
					row_column[6].write(item.role)
					details_column = row_column[7]

					if details_column.button(label="Details", type="primary", key=f'user-{item.id}-action'):
						if details_callback:
							details_callback(item)
			elif is_vm_list:
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

				if details_column.button(label="Details", type="secondary", key=f'vm-{item.id}-action'):
					if details_callback:
						details_callback(item)

				if connect_column.button(label="Connect", type="primary", key=f'vm-{item.id}-connect'):
					if connect_callback:
						connect_callback(item)
			else:
				# Bookmark data
				item: Bookmark = item
				row_column[0].write(item.id)
				row_column[1].write(item.name)
				row_column[2].write(item.link)

				details_column = row_column[3]

				if details_column.button(label="Details", type="secondary", key=f'bookmark-{item.id}-action'):
					if details_callback:
						details_callback(item)


def render_sidebar_menu(role: Role | None):
	"""
	Renders the sidebar menu based on the user's role stored in the session state.

	https://docs.streamlit.io/develop/tutorials/multipage/st.page_link-nav
	"""
	with st.sidebar:
		st.title("vm-lab")
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


def confirm_in_page(
		bordered_container: bool = True, text: str = None, caption: str = None,
		confirm_button_label: str = "Yes", cancel_button_label: str = "Cancel",
		is_confirm_button_type_primary: bool = False, is_cancel_button_type_primary: bool = False,
		confirm_button_callback: Callable = None, cancel_button_callback: Callable = None
):
	"""
	https://discuss.streamlit.io/t/add-cancel-button-to-close-modal/87318
	Renders a confirmation *section* with a description and two buttons with custom behavior.

	:param bordered_container: Whether to render the container with a border
	:param text: The description displayed on top of the dialog (not the title)
	:param caption: The caption (muted text) displayed below the description
	:param confirm_button_label: The label for the button to confirm
	:param cancel_button_label: The label for the button to cancel
	:param is_confirm_button_type_primary: Whether to render the confirm button as primary
	:param is_cancel_button_type_primary: Whether to render the cancel button as primary
	:param confirm_button_callback: The callback for the confirm button
	:param cancel_button_callback: The callback for the cancel button
	"""
	with st.container(border=bordered_container):
		if text:
			st.markdown(text)
		if caption:
			st.caption(caption)

		confirm_button_type = "secondary"
		if is_confirm_button_type_primary:
			confirm_button_type = "primary"

		cancel_button_type = "secondary"
		if is_cancel_button_type_primary:
			cancel_button_type = "primary"

		confirm_column, cancel_column = st.columns(2)

		with confirm_column:
			if st.button(confirm_button_label, use_container_width=True, type=confirm_button_type,
					  on_click=confirm_button_callback):
				st.rerun()

		with cancel_column:
			if st.button(cancel_button_label, use_container_width=True, type=cancel_button_type,
					  on_click=cancel_button_callback):
				st.rerun()


@st.dialog("Confirm")
def confirm_dialog(
		text: str = None, caption: str = None,
		confirm_button_label: str = "Yes", cancel_button_label: str = "Cancel",
		is_confirm_button_type_primary: bool = False, is_cancel_button_type_primary: bool = False,
		confirm_button_callback: Callable = None, cancel_button_callback: Callable = None
):
	"""
	https://discuss.streamlit.io/t/add-cancel-button-to-close-modal/87318
	Renders a confirmation *dialog* with a description and two buttons with custom behavior.

	NOTE: This does not work when called inside another dialog. Use `confirm_in_page`.

	:param text: The description displayed on top of the dialog (not the title)
	:param caption: The caption (muted text) displayed below the description
	:param confirm_button_label: The label for the button to confirm
	:param cancel_button_label: The label for the button to cancel
	:param is_confirm_button_type_primary: Whether to render the confirm button as primary
	:param is_cancel_button_type_primary: Whether to render the cancel button as primary
	:param confirm_button_callback: The callback for the confirm button
	:param cancel_button_callback: The callback for the cancel button
	"""
	confirm_in_page(
		bordered_container=False,
		text=text,
		caption=caption,
		confirm_button_label=confirm_button_label,
		cancel_button_label=cancel_button_label,
		is_confirm_button_type_primary=is_confirm_button_type_primary,
		is_cancel_button_type_primary=is_cancel_button_type_primary,
		confirm_button_callback=confirm_button_callback,
		cancel_button_callback=cancel_button_callback
	)

