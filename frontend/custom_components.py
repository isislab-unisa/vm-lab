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
	** DEPRECATED **
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


def render_sidebar_menu(role: Role | None, name: str | None):
	"""
	Renders the sidebar menu based on the user's role stored in the session state.

	https://docs.streamlit.io/develop/tutorials/multipage/st.page_link-nav
	"""
	with st.sidebar:
		st.title("VM Lab")
		if name:
			st.caption(name)

		match role:
			case Role.NEW_USER:
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.USER:
				st.page_link(PageNames.my_vms, label="My Dashboard")
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.MANAGER:
				st.page_link(PageNames.my_vms, label="My Dashboard")
				st.page_link(PageNames.manage_users, label="Manage Users")
				st.page_link(PageNames.waiting_list, label="Waiting List")
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.ADMIN:
				st.page_link(PageNames.my_vms, label="My Dashboard")
				st.page_link(PageNames.manage_users, label="Manage Users")
				st.page_link(PageNames.waiting_list, label="Waiting List")
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


def interactive_data_table(key: str, data: list[dict],
						   column_settings: dict, button_settings: dict,
						   popover_settings: dict = None, filters_expanded: bool = False,
						   refresh_data_callback: Callable = None, clear_filters_button: bool = True,
						   title: str | None = None, action_header_name: str | None = "Actions"):
	"""
	Full documentation here:
	https://github.com/isislab-unisa/vm-lab/wiki/Component-%E2%80%90-Interactive-Data-Table

	:param key: The unique key to give to this table's elements.
	:param data: The data to display in the table.
    :param refresh_data_callback: A function to call when the Refresh button in the filters is pressed.
	:param column_settings: Describes how should the columns be.
	:param button_settings: Describes what buttons should be included for each row.
	:param popover_settings: If defined, shows a popover button containing all the buttons.
	:param filters_expanded: Whether the filters are expanded or not.
	:param clear_filters_button: Whether to display the "Clear Filters" button in the filters' menu.
	:param title: The title to display above the table.
	:param action_header_name: The string to show in the header of the buttons' header.
	:raises ValueError: If `data_name` is not defined in a `column_settings` entry.
	"""

	# Write the title
	if title is not None:
		st.title(title)
		st.divider()

	# List with column names
	display_names = list(column_settings.keys())

	# List with column widths
	widths = []
	for name in display_names:
		column_width: int = column_settings.get(name).get("column_width", 1)
		widths.append(column_width)

	# Default filtered data is all the data
	filtered_data = data

	# Filters
	with st.expander("Filters", expanded=filters_expanded):
		filters_buttons_col1, filters_buttons_col2 = st.columns(2)

		# Refresh/Clear buttons
		with filters_buttons_col1:
			if refresh_data_callback is not None and st.button(
					":material/Refresh: Refresh Data",
					use_container_width=True,
					key=f"{key}-refresh-data-button",
			):
				st.cache_data.clear()
				filtered_data = refresh_data_callback()

		with filters_buttons_col2:
			if clear_filters_button and st.button(
					":material/Clear_All: Clear Filters",
					use_container_width=True,
					key=f"{key}-clear-filters-button",
			):
				# Clear the inputs
				st.session_state[f"{key}-search_selectbox"] = display_names[0]
				st.session_state[f"{key}-search_query"] = ""

		# Search Bars
		search_column = st.selectbox("Select column to search",
									 display_names,
									 key=f"{key}-search_selectbox")
		search_query = st.text_input("Search",
									 "",
									 key=f"{key}-search_query")

		# Search in the entire data list
		if search_query:
			data_name_to_search: str | None = column_settings.get(search_column).get("data_name", None)
			if data_name_to_search is None:
				raise ValueError(f"data_name must be defined in column_settings for '{search_column}'")

			filtered_data = []
			for row in data:
				if search_query.lower() in str(row[data_name_to_search]).lower():
					filtered_data.append(row)

	# Write the Header Row
	columns_header = st.columns(widths + [1])

	for index, name in enumerate(display_names):
		#columns_header[index].markdown(f'<div style="text-align: center"><b>{name}</b></div>', unsafe_allow_html=True)
		columns_header[index].markdown(f"<u>**{name}**</u>", unsafe_allow_html=True)

	if action_header_name is not None:
		columns_header[-1].wrimarkdownte(f"<u>**{action_header_name}**</u>", unsafe_allow_html=True)

	if len(filtered_data) == 0:
		with st.container():
			st.caption("No data")
		return

	# Write all the Rows
	for data_index, data_row in enumerate(filtered_data):
		columns_row = st.columns(widths + [1])

		# Data Columns
		for index, name in enumerate(display_names):
			data_name = column_settings.get(name).get("data_name", None)
			if data_name is None:
				raise ValueError(f"data_name must be defined in column_settings for '{name}'")

			columns_row[index].write(data_row[data_name])

		# Action Buttons Column
		with columns_row[-1]:
			if popover_settings is not None:
				popover_text = popover_settings.get("text", "Open")
				popover_icon = popover_settings.get("icon", None)
				with st.popover(popover_text, icon=popover_icon):
					render_buttons(button_settings, data_index, data_row, key, True)
			else:
				render_buttons(button_settings, data_index, data_row, key, False)


def render_buttons(button_settings, data_index, data_row, key, use_width):
	all_disabled_buttons = data_row.get("buttons_disabled", None)
	for button_label, button_configuration in button_settings.items():
		button_type = "primary" if button_configuration.get("primary", False) else "secondary"
		if all_disabled_buttons is None:
			button_disabled = False
		else:
			button_disabled = all_disabled_buttons.get(button_label, False)

		button_icon = button_configuration.get("icon", None)
		show_only_icon = button_configuration.get("show_only_icon", False)
		button_help = button_configuration.get("help", None)

		if show_only_icon and button_icon is not None:
			button_label_to_show = button_icon  # Show only the icon
		elif show_only_icon and button_icon is None:
			button_label_to_show = button_label  # There is no icon to show, so show only the label
		else:
			button_label_to_show = f"{button_icon} {button_label}"  # Show icon and label

		if st.button(key=f"{key}_button_{button_label}_{data_index}",
					 label=button_label_to_show,
					 type=button_type,
					 disabled=button_disabled,
					 help=button_help,
					 use_container_width=use_width):
			button_callback = button_configuration.get("callback", None)
			if not button_disabled and button_callback is not None:
				button_callback(data_row=data_row)
