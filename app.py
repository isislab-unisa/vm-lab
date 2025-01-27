from typing import Callable

import streamlit as st
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine
from frontend.page_names import PageNames

#switch_page(PageNames.my_vms)
if st.button("Go to my vms", type="primary"):
	switch_page(PageNames.my_vms)


@st.cache_data
def my_mock_db():
	with get_db() as db_list:
		print("Accessing db")
		vm_list = VirtualMachine.find_all(db_list)

	result = []
	for vm in vm_list:
		vm_dict = {
			"id": vm.id,
			"name": vm.name,
			"buttons_disabled": {
				"Edit": False,
				"Delete": True,
				"Connect": False
			}
		}
		print(vm_dict)
		result.append(vm_dict)

	return result


def better_table(data, column_settings, button_settings, title="Table",
				 refresh_data_callback: Callable = None, clear_filters_button: bool = True):
	"""
	:param data: A list of dictionaries containing the data to display.
	:param column_settings: Configuration of the columns. Each key is the column title, and the value is a dictionary with:
	    - "column_width": The width of the column.
	    - "data_name": The name of the field in the data dictionary.
	:param button_settings: Configuration of the buttons. Each key is the button name, and the value is a dictionary with:
	    - "primary": Indicates if the button is primary.
	    - "callback": The callback function to be called when the button is clicked.
	"""

	# Write the title
	st.write(f"### {title}")
	st.write("---")

	# List with column names
	display_names = list(column_settings.keys())

	# List with column widths
	widths = []
	for name in display_names:
		widths.append(column_settings[name]["column_width"])

	# Default filtered data is all the data
	filtered_data = data

	# Filters
	with st.expander("Filters"):
		filters_buttons_col1, filters_buttons_col2 = st.columns(2)

		# Refresh/Clear buttons
		with filters_buttons_col1:
			if refresh_data_callback is not None and st.button(":material/Refresh: Refresh Data", use_container_width=True):
				st.cache_data.clear()
				filtered_data = refresh_data_callback()

		with filters_buttons_col2:
			if clear_filters_button and st.button(":material/Clear_All: Clear Filters", use_container_width=True):
				st.session_state[f"{title}-search_selectbox"] = display_names[0]
				st.session_state[f"{title}-search_query"] = ""

		# Search Bars
		search_column = st.selectbox("Select column to search",
									 display_names,
									 key=f"{title}-search_selectbox")
		search_query = st.text_input("Search",
									 "",
									 key=f"{title}-search_query")

		# Search in the entire data list
		if search_query:
			data_name_to_search = column_settings[search_column]["data_name"]
			filtered_data = []
			for row in data:
				if search_query.lower() in str(row[data_name_to_search]).lower():
					filtered_data.append(row)

	# Write the Header Row
	columns_header = st.columns(widths + [1])

	for index, name in enumerate(display_names):
		columns_header[index].write(f"**{name}**")

	columns_header[-1].write("**Actions**")

	# Write all the Rows
	for data_index, data_row in enumerate(filtered_data):
		columns_row = st.columns(widths + [1])

		# Data Columns
		for index, name in enumerate(display_names):
			data_name = column_settings[name]["data_name"]
			columns_row[index].write(data_row[data_name])

		# Action Buttons Column
		with columns_row[-1]:
			for button_label, button_configuration in button_settings.items():
				button_type = "primary" if button_configuration.get("primary", False) else "secondary"
				button_disabled = data_row["buttons_disabled"].get(button_label, False)

				button_icon = button_configuration.get("icon", "")
				show_only_icon = button_configuration.get("show_only_icon", False)

				button_help = button_configuration.get("help", None)

				if show_only_icon and button_icon != "":
					button_label_to_show = button_icon # Show only the icon
				elif show_only_icon and button_icon == "":
					button_label_to_show = button_label # There is no icon to show, so show only the label
				else:
					button_label_to_show = f"{button_icon} {button_label}" # Show icon and label

				if st.button(key=f"{title}_{button_label}_{data_index}",
							 label=button_label_to_show,
							 type=button_type,
							 disabled=button_disabled,
							 help=button_help):
					if not button_disabled:
						button_configuration["callback"](data_row=data_row)


@st.dialog("Edit")
def edit_callback(data_row):
	st.write(f"**Editing** user {data_row['name']} with ID {data_row['id']}")

@st.dialog("Delete")
def delete_callback(data_row):
	st.write(f"**Deleting** user {data_row['name']} with ID {data_row['id']}")

@st.dialog("Delete")
def connect_callback(data_row):
	st.write(f"**Calling** user {data_row['name']} with ID {data_row['id']}")


better_table(
	data=my_mock_db(),
	refresh_data_callback=my_mock_db,
	column_settings={
		"VM ID": {
			"column_width": 1,
			"data_name": "id"
		},
		"Name": {
			"column_width": 2,
			"data_name": "name"
		},
	},
	button_settings={
		"Edit": {
			"primary": False,
			"callback": edit_callback,
			"icon": ":material/Edit:",
			"show_only_icon": False,
			"help": "Edit this"
		},
		"Delete": {
			"primary": False,
			"callback": delete_callback,
			"icon": ":material/Delete:",
			"show_only_icon": False,
			"help": "Delete this"
		},
		"Connect": {
			"primary": True,
			"callback": connect_callback,
			"icon": ":material/Arrow_Forward:",
			"show_only_icon": False
		}
	},
)