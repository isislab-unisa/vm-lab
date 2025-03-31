import streamlit as st

from backend.role import Role
from frontend.page_names import PageNames


def sidebar_menu(role: Role | None, full_name: str | None):
	"""
	Renders the sidebar menu based on the user's role stored in the session state.

	https://docs.streamlit.io/develop/tutorials/multipage/st.page_link-nav
	"""
	with st.sidebar:
		st.title("VM Lab")

		if full_name:
			st.caption(f"{full_name} - {role.to_phrase()}")

		match role:
			case Role.NEW_USER:
				st.page_link(
					page=PageNames.USER_SETTINGS.file_name,
					label=PageNames.USER_SETTINGS.label
				)
				st.page_link(
					page=PageNames.LOGOUT.file_name,
					label=PageNames.LOGOUT.label
				)

			case Role.REGULAR:
				st.page_link(
					page=PageNames.MAIN_DASHBOARD.file_name,
					label=PageNames.MAIN_DASHBOARD.label
				)
				st.page_link(
					page=PageNames.USER_SETTINGS.file_name,
					label=PageNames.USER_SETTINGS.label
				)
				st.page_link(
					page=PageNames.LOGOUT.file_name,
					label=PageNames.LOGOUT.label
				)

			case Role.SIDEKICK:
				st.page_link(
					page=PageNames.MAIN_DASHBOARD.file_name,
					label=PageNames.MAIN_DASHBOARD.label
				)
				st.page_link(
					page=PageNames.USER_SETTINGS.file_name,
					label=PageNames.USER_SETTINGS.label
				)
				st.page_link(
					PageNames.LOGOUT.file_name,
					label=PageNames.LOGOUT.label
				)

			case Role.MANAGER:
				st.page_link(
					page=PageNames.MAIN_DASHBOARD.file_name,
					label=PageNames.MAIN_DASHBOARD.label
				)
				st.page_link(
					page=PageNames.MANAGE_USER_LIST.file_name,
					label=PageNames.MANAGE_USER_LIST.label
				)
				st.page_link(
					page=PageNames.MANAGE_WAITING_LIST.file_name,
					label=PageNames.MANAGE_WAITING_LIST.label
				)
				st.page_link(
					page=PageNames.USER_SETTINGS.file_name,
					label=PageNames.USER_SETTINGS.label
				)
				st.page_link(
					page=PageNames.LOGOUT.file_name,
					label=PageNames.LOGOUT.label
				)

			case Role.ADMIN:
				st.page_link(
					page=PageNames.MAIN_DASHBOARD.file_name,
					label=PageNames.MAIN_DASHBOARD.label
				)
				st.page_link(
					page=PageNames.MANAGE_USER_LIST.file_name,
					label=PageNames.MANAGE_USER_LIST.label
				)
				st.page_link(
					page=PageNames.MANAGE_WAITING_LIST.file_name,
					label=PageNames.MANAGE_WAITING_LIST.label
				)
				st.page_link(
					page=PageNames.USER_SETTINGS.file_name,
					label=PageNames.USER_SETTINGS.label
				)
				st.page_link(
					page=PageNames.LOGOUT.file_name,
					label=PageNames.LOGOUT.label
				)

			case _:  # Not logged in
				st.page_link(
					page=PageNames.LOGIN.file_name,
					label=PageNames.LOGIN.label
				)
				st.page_link(
					page=PageNames.REGISTER.file_name,
					label=PageNames.REGISTER.label
				)
				st.page_link(
					page=PageNames.FORGOT_CREDENTIALS.file_name,
					label=PageNames.FORGOT_CREDENTIALS.label
				)
