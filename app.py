from typing import Callable

import streamlit as st
from streamlit import switch_page

from frontend.custom_components import confirm_dialog, confirm_in_page
from frontend.page_names import PageNames

#switch_page(PageNames.my_vms)
if st.button("Go to my vms", type="primary"):
	switch_page(PageNames.my_vms)


def my_printer(something):
	print(something)


if st.button("Confirm in page"):
	confirm_in_page(
		confirm_button_callback=lambda: my_printer("Yes in page"),
		cancel_button_callback=lambda: my_printer("No in page"),
	)


if st.button("Confirm dialog"):
	confirm_dialog(
		confirm_button_callback=lambda: my_printer("Yes in dialog"),
		cancel_button_callback=lambda: my_printer("No in dialog"),
	)



