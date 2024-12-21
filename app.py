import streamlit as st
from streamlit import switch_page

from frontend.custom_components import confirm_dialog
from frontend.page_names import PageNames

#switch_page(PageNames.my_vms)
if st.button("Go to my vms"):
	switch_page(PageNames.my_vms)


def my_printer(something):
	print(something)


if st.button("Confirm"):
	confirm_dialog(
		confirm_button_callback=lambda: my_printer("Yes"),
	)



