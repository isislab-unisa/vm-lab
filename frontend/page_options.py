import streamlit as st

from enum import Enum
from typing import Literal
from streamlit import switch_page
from streamlit_authenticator import Authenticate

from backend.role import Role
from backend.authentication import is_logged_in, get_current_user_role, get_or_create_authenticator_object, \
	get_current_user_full_name
from frontend.custom_components import render_sidebar_menu
from frontend.page_names import PageNames


class AccessControlType(Enum):
	"""
	FREE_ACCESS: All users have unrestricted access.

	LOGGED_IN_ONLY: Access is restricted to logged-in users.

	UNREGISTERED_ONLY: Access is restricted to unregistered users.

	ACCEPTED_ROLES_ONLY: Only users with specified roles in `accepted_roles` can access.
	"""
	LOGGED_IN_ONLY = "logged_in_only"
	UNREGISTERED_ONLY = "unregistered_only"
	ACCEPTED_ROLES_ONLY = "accepted_roles_only"
	FREE_ACCESS = "free_access"


def page_setup(layout: Literal["centered", "wide"] = "wide",
			   title: str = None,
			   access_control: Literal[
				   AccessControlType.FREE_ACCESS,
				   AccessControlType.LOGGED_IN_ONLY,
				   AccessControlType.UNREGISTERED_ONLY,
				   AccessControlType.ACCEPTED_ROLES_ONLY
			   ] = AccessControlType.FREE_ACCESS,
			   accepted_roles: list[Role] = None,
			   callback=None,
			   print_session_state: bool = False,
			   logged_in_not_accepted_redirect: str = PageNames.my_vms,
			   unregistered_not_accepted_in_redirect: str = PageNames.login,
			   role_not_accepted_redirect: str = PageNames.error,
			   new_user_redirect_to_wait_page: bool = True
			   ) -> Authenticate:
	"""
	Configures the page layout, title, and access control for the current page, including authentication
    and authorization checks, optional callbacks, and session debugging.

	:param layout: Sets the page layout; either "centered" (content centered) or "wide" (wider view). Default is "wide".
	:param title: Title of the page, displayed in the browser tab. If `None`, the title will be the file name.
	:param access_control: Defines access control settings with `AccessControlType`.
	:param accepted_roles: List of `Roles` granted access when `access_control` is set to `ACCEPTED_ROLES_ONLY`.
	:param callback: Optional function executed after access control checks.
	:param print_session_state: If `True`, the current session_state is printed for debugging. Default is `False`.
	:param logged_in_not_accepted_redirect: Page to redirect to if a logged-in user is not accepted. Default is `PageNames.my_vms`.
	:param unregistered_not_accepted_in_redirect: Page to redirect to if an unregistered user attempts to access a restricted page. Default is `PageNames.login`.
	:param role_not_accepted_redirect: Page to redirect to if the user's role does not match `accepted_roles`. Default is `PageNames.error`.
	:param new_user_redirect_to_wait_page: If `True`, new users are redirected to a wait page if their role is not accepted. Default is `True`.
	:return: Returns a streamlit-authentication authenticator object.
	"""

	# Authentication
	authenticator = get_or_create_authenticator_object()
	authenticator.login(location='unrendered')  # Attempt to log in with cookie
	logged_in = is_logged_in()
	role = get_current_user_role()
	name = get_current_user_full_name()

	# Authorization
	match access_control:
		case AccessControlType.UNREGISTERED_ONLY:
			if logged_in:
				switch_page(logged_in_not_accepted_redirect)

		case AccessControlType.LOGGED_IN_ONLY:
			if not logged_in:
				switch_page(unregistered_not_accepted_in_redirect)

		case AccessControlType.ACCEPTED_ROLES_ONLY:
			if accepted_roles is None:
				raise ValueError("accepted_roles must not be None when access_control is ACCEPTED_ROLES_ONLY")

			if not logged_in:
				switch_page(unregistered_not_accepted_in_redirect)

			if role not in accepted_roles:
				if new_user_redirect_to_wait_page and role == Role.NEW_USER:
					switch_page(PageNames.wait)

				switch_page(role_not_accepted_redirect)

		case _:
			# Free Access to the page
			pass

	# Callback function
	if callback is not None:
		callback()

	# Title and Layout
	if title:
		st.set_page_config(layout=layout, page_title=title)
	else:
		st.set_page_config(layout=layout)

	# Sidebar
	render_sidebar_menu(role, name)

	# Debug
	if print_session_state:
		st.write(st.session_state)

	return authenticator


