from typing import Callable

import streamlit as st


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
