import streamlit as st


def build_error(intro: str, when: str, cause: str):
	def clean_when(s):
		if len(s) == 0:
			return s
		else:
			# Add a space and lower the first character of the "when" string
			return f" {s[0].lower() + s[1:]}"

	return f"**{intro}{clean_when(when)}:**\n\n{cause}"


def handle_unknown_exception(unknown_exception):
	return f"An error ({type(unknown_exception)}) has occurred", str(unknown_exception)


def error_message(
		intro: str = "An error has occurred",
		when: str = "",
		cause: str = "Unknown Error.",
		unknown_exception: BaseException = None):
	if unknown_exception:
		intro, cause = handle_unknown_exception(unknown_exception)

	st.error(build_error(intro, when, cause))


def error_toast(
		intro: str = "An error has occurred",
		when: str = "",
		cause: str = "Unknown Error.",
		unknown_exception: BaseException = None):
	if unknown_exception:
		intro, cause = handle_unknown_exception(unknown_exception)

	st.toast(f":red[{build_error(intro, when, cause)}]")