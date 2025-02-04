from typing import Literal

import streamlit as st
from streamlit import switch_page
from streamlit_authenticator import Authenticate

from backend.authentication import is_logged_in, get_current_user_role, get_or_create_authenticator_object, \
	get_current_user_full_name, get_current_user_name, get_current_user_email
from backend.database import get_db
from backend.models import User
from backend.role import Role, role_in_white_list
from frontend.page_names import PageNames


class PageSessionData:
	def __init__(self, authenticator: Authenticate, logged_in: bool,
				 user_role: Role, user_name: str, user_full_name: str, user_email: str):
		"""
		A class that represents the session data of a page.
		It contains information about authentication, login status, and user details.
		:param authenticator: The streamlit-authenticator object
		:param logged_in: Whether the user is logged-in or not
		:param user_role: The role of the current user
		:param user_name: The username of the current user
		:param user_full_name: The full name of the current user
		:param user_email: The email of the current user
		"""
		self.authenticator = authenticator
		self.logged_in = logged_in

		self.user_role = user_role
		self.user_name = user_name
		self.user_full_name = user_full_name
		self.user_email = user_email

	def get_user(self):
		"""Obtain the object of the current user or `None` if it wasn't found."""
		with get_db() as db:
			if self.user_name:
				return User.find_by_user_name(db, self.user_name)
			elif self.user_email:
				return User.find_by_email(db, self.user_email)
			else:
				return None



def page_setup(layout: Literal["centered", "wide"] = "wide",
			   title: str = None,
			   access_control: Literal[
				   "logged_in_only",
				   "unregistered_only",
				   "accepted_roles_only",
				   "free_access"
			   ] = "free_access",
			   accepted_roles: list[Role] = None,
			   callback=None,
			   print_session_state: bool = False,
			   logged_in_not_accepted_redirect: str = PageNames.my_vms,
			   unregistered_not_accepted_in_redirect: str = PageNames.login,
			   role_not_accepted_redirect: str = PageNames.error,
			   new_user_redirect_to_wait_page: bool = True
			   ) -> PageSessionData:
	"""
	Configures the page layout, title, and access control for the current page, including authentication
    and authorization checks, optional callbacks, and session debugging.

	:param layout: Sets the page layout; either "centered" (content centered) or "wide" (wider view).
	:param title: Title of the page, displayed in the browser tab. If `None`, the title will be the file name.
	:param access_control: Defines access control settings:
	- "free_access" (default): All users have unrestricted access.
	- "logged_in_only": Access is restricted to logged-in users.
	- "unregistered_only": Access is restricted to unregistered users.
	- "accepted_roles_only": Only users with specified roles in `accepted_roles` can access.
	:param accepted_roles: List of `Roles` granted access when `access_control` is set to "accepted_roles_only".
	:param callback: Optional function executed after access control checks.
	:param print_session_state: If `True`, the current session_state is printed at the start of the page for debugging.
	:param logged_in_not_accepted_redirect: Page to redirect to if a logged-in user is not accepted.
	:param unregistered_not_accepted_in_redirect: Page to redirect to if an unregistered user attempts to access a restricted page.
	:param role_not_accepted_redirect: Page to redirect to if the user's role does not match `accepted_roles`.
	:param new_user_redirect_to_wait_page: If `True`, new users are redirected to a wait page if their role is not accepted.

	:return: Returns an instance of `PageSessionData` that holds the information for the session on the current page.
	"""

	# Authentication
	authenticator = get_or_create_authenticator_object()
	authenticator.login(location='unrendered')  # Attempt to log in with cookie

	user_is_logged_in = is_logged_in()
	user_role = get_current_user_role()
	user_name = get_current_user_name()
	user_full_name = get_current_user_full_name()
	user_email = get_current_user_email()

	# Authorization
	match access_control:
		case "unregistered_only":
			if user_is_logged_in:
				switch_page(logged_in_not_accepted_redirect)

		case "logged_in_only":
			if not user_is_logged_in:
				switch_page(unregistered_not_accepted_in_redirect)

		case "accepted_roles_only":
			if accepted_roles is None:
				raise ValueError("accepted_roles must not be None when access_control is 'accepted_roles_only'")

			if not user_is_logged_in:
				switch_page(unregistered_not_accepted_in_redirect)

			if not role_in_white_list(user_role, accepted_roles):
				if user_role == Role.NEW_USER and new_user_redirect_to_wait_page:
					switch_page(PageNames.wait)
				else:
					switch_page(role_not_accepted_redirect)

		case _:
			# Free access to ANYONE for the page
			pass

	# Callback function executed after authorization
	if callback is not None:
		callback()

	# Title and Layout
	if title:
		st.set_page_config(layout=layout, page_title=title)
	else:
		st.set_page_config(layout=layout)

	# Sidebar
	render_sidebar_menu(user_role, user_full_name)

	# Debug
	if print_session_state:
		st.write(st.session_state)

	return PageSessionData(
		authenticator=authenticator,
		logged_in=user_is_logged_in,
		user_role=user_role,
		user_name=user_name,
		user_full_name=user_full_name,
		user_email=user_email,
	)


def render_sidebar_menu(role: Role | None, full_name: str | None):
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
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.SIDEKICK:
				st.page_link(PageNames.my_vms, label="My Dashboard")
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.MANAGER:
				st.page_link(PageNames.my_vms, label="My Dashboard")
				st.page_link(PageNames.manage_users, label="Manage Users")
				st.page_link(PageNames.waiting_list, label="Waiting List")
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case Role.ADMIN:
				st.page_link(PageNames.my_vms, label="My Dashboard")
				st.page_link(PageNames.manage_users, label="Manage Users")
				st.page_link(PageNames.waiting_list, label="Waiting List")
				st.page_link(PageNames.user_settings, label="Settings")
				st.page_link(PageNames.logout, label="Logout")

			case _:  # Not logged in
				st.page_link(PageNames.login, label="Login")
				st.page_link(PageNames.register, label="Register")
				st.page_link(PageNames.forgot_credentials, label="Forgot Credentials")
