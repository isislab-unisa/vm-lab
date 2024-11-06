from typing import Optional, List

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate, RegisterError
from streamlit_authenticator.controllers import AuthenticationController
from streamlit_authenticator.utilities import Validator, Helpers

from backend.database import get_db_users_credentials, get_db
from backend.roles import Roles
from frontend.page_names import PageNames
from utils.session_state import in_session_state, set_session_state, get_session_state
from backend.database import User


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


def find_unauthorized_redirect_page(accepted_roles: list[str] = None) -> str | None:
	"""
	If the user is not authorized, find the page name of the redirect, otherwise returns None.
	"""
	authenticator = get_authenticator_object()
	authenticator.login(location='unrendered')  # Attempt to log in with cookie

	# User not logged in
	if not is_logged_in():
		return PageNames.login

	# User logged in but not authorized
	role = get_session_state('roles')
	if (accepted_roles is not None
			and not is_role_accepted(role, accepted_roles)):
		set_session_state('error_message', 'Not authorized')
		return PageNames.error

	# User logged in and authorized
	return None


def register_new_user(new_first_name: str, new_last_name: str, new_email: str,
                      new_username: str, new_password: str, new_password_repeat: str,
                      captcha: bool=True, entered_captcha: Optional[str]=None, domains: Optional[List[str]]=None):
	validator = Validator()

	new_first_name = new_first_name.strip()
	new_last_name = new_last_name.strip()
	new_email = new_email.strip()
	new_username = new_username.lower().strip()
	new_password = new_password.strip()
	new_password_repeat = new_password_repeat.strip()

	if not validator.validate_name(new_first_name):
		raise RegisterError('First name is not valid')

	if not validator.validate_name(new_last_name):
		raise RegisterError('Last name is not valid')

	if not validator.validate_email(new_email):
		raise RegisterError('Email is not valid')

	if domains:
		if new_email.split('@')[1] not in ' '.join(domains):
			raise RegisterError('Email not allowed to register')

	if not validator.validate_username(new_username):
		raise RegisterError('Username is not valid')

	if (not validator.validate_length(new_password, 1)
			or not validator.validate_length(new_password_repeat, 1)):
		raise RegisterError('Password/repeat password fields cannot be empty')

	if new_password != new_password_repeat:
		raise RegisterError('Passwords do not match')

	if not validator.validate_password(new_password):
		raise RegisterError('Password does not meet criteria')

	if captcha:
		if not entered_captcha:
			raise RegisterError('Captcha not entered')

		entered_captcha = entered_captcha.strip()
		if not Helpers.check_captcha('register_user_captcha', entered_captcha):
			raise RegisterError('Captcha entered incorrectly')

	print("Everything seems fine")

	new_user = User(
		first_name=new_first_name,
		last_name=new_last_name,
		username=new_username,
		password=User.hash_password(new_password),
		email=new_email,
		role=Roles.USER,
	)

	with get_db() as db:
		db.add(new_user)
		db.commit()
		db.refresh(new_user)

	print("New user created:", new_user)

	create_authenticator_object()