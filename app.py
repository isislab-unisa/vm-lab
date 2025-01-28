import streamlit as st
from streamlit import switch_page

from backend.database import get_db
from backend.models import VirtualMachine
from frontend.custom_components import interactive_data_table
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


@st.dialog("Edit")
def edit_callback(data_row):
	st.write(f"**Editing** user {data_row['name']} with ID {data_row['id']}")

@st.dialog("Delete")
def delete_callback(data_row):
	st.write(f"**Deleting** user {data_row['name']} with ID {data_row['id']}")

@st.dialog("Delete")
def connect_callback(data_row):
	st.write(f"**Calling** user {data_row['name']} with ID {data_row['id']}")


interactive_data_table(
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