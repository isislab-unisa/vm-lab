from typing import Literal

import streamlit as st
from streamlit import switch_page

from backend.authentication import find_unauthorized_redirect_page, is_logged_in
from frontend.page_names import PageNames
from backend.roles import Roles
from utils.session_state import get_session_state


def page_setup(layout: Literal["centered", "wide"] = "wide",
			   title: str = None,
			   print_session_state: bool = False,
			   is_restricted: bool = True,
			   accepted_roles: list[str] = None):
	"""
	Must be one of the first function calls in the page.
	:param layout: The layout configuration for the page. Options are "centered" or "wide".
	:param title: The title of the page. If not provided, no title will be set.
	:param print_session_state: Output the current session state on top of the page.
	:param is_restricted: Enforces access control based on roles.
	:param accepted_roles: List of roles that are permitted to access the page. Used in conjunction with is_restricted.
	"""

	# Authorization
	if is_restricted:
		redirect_page = find_unauthorized_redirect_page(accepted_roles)
		if redirect_page:
			switch_page(redirect_page)

	# Title and Layout
	if title:
		st.set_page_config(layout=layout, page_title=title)
	else:
		st.set_page_config(layout=layout)

	# Sidebar
	render_sidebar_menu()

	# Debug
	if print_session_state:
		st.write(st.session_state)


def render_sidebar_menu():
	"""Renders the sidebar menu based on the user's role stored in the session state."""
	with st.sidebar:
		role = get_session_state('roles')

		match role:
			case Roles.NEW_USER:
				st.page_link(PageNames.logout, label="Logout")

			case Roles.USER:
				st.page_link(PageNames.my_vms, label="My VMs")
				st.page_link(PageNames.logout, label="Logout")

			case Roles.MANAGER:
				st.page_link(PageNames.my_vms, label="My VMs")
				st.page_link(PageNames.manage_users, label="Manage Users")
				st.page_link(PageNames.logout, label="Logout")

			case Roles.ADMIN:
				st.page_link(PageNames.my_vms, label="My VMs")
				st.page_link(PageNames.manage_users, label="Manage Users")
				st.page_link(PageNames.logout, label="Logout")

			case _:
				st.page_link(PageNames.login, label="Login")
				st.page_link(PageNames.register, label="Register")
				st.page_link(PageNames.forgot_credentials, label="Forgot Credentials")
