import streamlit as st
import streamlit_authenticator as stauth
from streamlit import switch_page
from streamlit_authenticator import Authenticate

from backend.database import get_db_users_credentials
from frontend.page_names import PageNames
from utils.session_state import in_session_state, set_session_state, get_session_state


def create_authenticator_object() -> Authenticate:
	"""Creates a streamlit-authenticator object and stores it in the session state."""
	credentials = get_db_users_credentials()
	cookie_name = st.secrets['cookie_name']
	cookie_key = st.secrets['cookie_key']
	cookie_expiry_days = st.secrets['cookie_expiry_days']

	authenticator: Authenticate = stauth.Authenticate(
		credentials=credentials,
		cookie_name=cookie_name,
		cookie_key=cookie_key,
		cookie_expiry_days=cookie_expiry_days
	)

	set_session_state('authenticator', authenticator)
	return authenticator


def get_authenticator_object() -> Authenticate:
	"""Retrieves the streamlit-authenticator object in the session state."""
	if not in_session_state('authenticator'):
		return create_authenticator_object()
	else:
		return get_session_state('authenticator')


def is_role_accepted(role: str, accepted_roles: list[str]) -> bool:
	"""Check if a role is in the list of accepted roles"""
	return role in accepted_roles


def is_logged_in() -> bool:
	"""Check whether the user is logged in"""
	if get_session_state('authentication_status'):
		return True
	else:
		# Status is None or False
		return False


def check_unauthorized_redirect_page(accepted_roles: list[str] = None) -> str | None:
	"""
	If the user is not authorized, find the page name of the redirect, otherwise returns None.
	"""
	authenticator = get_authenticator_object()
	authenticator.login(location='unrendered')  # Attempt to log in with cookie

	# User not logged in
	if not is_logged_in():
		return PageNames.login

	# User logged in but not authorized
	role = get_session_state('role')
	if (accepted_roles is not None
			and not is_role_accepted(role, accepted_roles)):
		set_session_state('error_message', 'Not authorized')
		return PageNames.error

	# User logged in and authorized
	return None
