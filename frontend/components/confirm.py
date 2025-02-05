from typing import Callable

import streamlit as st


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
