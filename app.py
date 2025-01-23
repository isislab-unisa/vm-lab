import streamlit as st
from streamlit import switch_page
from frontend.page_names import PageNames

#switch_page(PageNames.my_vms)
if st.button("Go to my vms", type="primary"):
	switch_page(PageNames.my_vms)


def better_table(data, column_settings, button_settings, title="Table"):
	"""
	:param data: A list of dictionaries containing the data to display.
	:param column_settings: Configuration of the columns. Each key is the column title, and the value is a dictionary with:
	    - "column_width": The width of the column.
	    - "data_name": The name of the field in the data dictionary.
	:param button_settings: Configuration of the buttons. Each key is the button name, and the value is a dictionary with:
	    - "primary": Indicates if the button is primary.
	    - "callback": The callback function to be called when the button is clicked.
	"""

	# my_css = """
	#     <style>
	#         .table-container {
	#             background-color: #333;
	#             color: #f1f1f1;
	#         }
	#         .table-container th, .table-container td {
	#             border-color: #444;
	#         }
	#         .button-primary {
	#             background-color: #3e8e41;
	#             color: white;
	#         }
	#         .button-secondary {
	#             background-color: #f44336;
	#             color: white;
	#         }
	#     </style>
	#     """
	#
	# st.markdown(my_css, unsafe_allow_html=True)

	# List with column names
	display_names = list(column_settings.keys())

	# Column widths
	widths = []
	for name in display_names:
		widths.append(column_settings[name]["column_width"])

	st.write(f"### {title}")
	st.write("---")

	# Header
	columns_header = st.columns(widths + [1])

	for index, name in enumerate(display_names):
		columns_header[index].write(f"**{name}**")

	columns_header[-1].write("**Actions**")

	# Rows
	for data_index, data_row in enumerate(data):
		columns_row = st.columns(widths + [1])

		# Data Columns
		for index, name in enumerate(display_names):
			data_name = column_settings[name]["data_name"]
			columns_row[index].write(data_row[data_name])

		# Action Buttons Column
		with columns_row[-1]:
			for button_label, button_configuration in button_settings.items():
				button_type = "primary" if button_configuration["primary"] else "secondary"

				if st.button(button_label, type=button_type, key=f"{title}_{button_label}_{data_index}"):
					button_configuration["callback"](data_row=data_row)


@st.dialog("Edit")
def edit_callback(data_row):
	st.write(f"**Editing** user {data_row['name']} with ID {data_row['id']}")

@st.dialog("Delete")
def delete_callback(data_row):
	st.write(f"**Deleting** user {data_row['name']} with ID {data_row['id']}")

@st.dialog("Delete")
def call_callback(data_row):
	st.write(f"**Calling** user {data_row['name']} with ID {data_row['id']}")

# Esempio di chiamata della funzione
mydata = [
	{
		"id": 1,
		"name": "Mario"
	},
	{
		"id": 2,
		"name": "Luigi"
	}
]

better_table(
	data=mydata,
	column_settings={
		"User ID": {
			"column_width": 1,
			"data_name": "id"
		},
		"Username": {
			"column_width": 3,
			"data_name": "name"
		},
	},
	button_settings={
		"Edit": {
			"primary": False,
			"callback": edit_callback
		},
		"Delete": {
			"primary": False,
			"callback": delete_callback
		},
		"Call": {
			"primary": True,
			"callback": call_callback
		}
	}
)


