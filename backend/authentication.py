import streamlit as st
import streamlit_authenticator as stauth

from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from streamlit_authenticator import Authenticate, RegisterError, UpdateError
from streamlit_authenticator.utilities import Validator, Helpers

from backend.database import get_db
from backend.models import User
from backend.role import Role
from utils.session_state import set_session_state_item, get_session_state_item


def get_db_users_credentials() -> dict:
	"""
    Gets all user credentials from the database and organizes them into a dictionary for use in streamlit-authentication.

    :return: A dictionary containing the usernames, emails, first names, last names, passwords, and roles for all
    users in the database.
    """
	credentials = {"usernames": {}}

	with get_db() as db:
		users = User.find_all(db)
		for user in users:
			credentials["usernames"][user.username] = user.to_credentials_dict()

	return credentials


def create_authenticator_object() -> Authenticate:
	"""Creates a streamlit-authenticator object and stores it in the session state."""
	credentials = get_db_users_credentials()

	cookie_name = st.secrets['cookie_name']
	cookie_key = st.secrets['cookie_key']
	cookie_expiry_days = st.secrets['cookie_expiry_days']

	authenticator = stauth.Authenticate(
		credentials=credentials,
		cookie_name=cookie_name,
		cookie_key=cookie_key,
		cookie_expiry_days=cookie_expiry_days
	)

	set_session_state_item('authenticator', authenticator)
	return authenticator


def get_or_create_authenticator_object() -> Authenticate:
	"""Returns the streamlit-authenticator object in the session state, or creates and returns a new one if it wasn't found."""
	authenticator = get_session_state_item('authenticator')

	if authenticator is None:
		authenticator = create_authenticator_object()

	return authenticator


def add_new_user_to_authenticator_object(new_user_data: User, replace_username: str = None) -> Authenticate:
	"""
	Updates the authenticator object stored in the current session by adding a new user.

	:param new_user_data: The new user data
	:param replace_username: Used by the "edit" version of this function to replace the data for an existing user
	"""
	authenticator: Authenticate = get_or_create_authenticator_object()
	credentials: dict = authenticator.authentication_controller.authentication_model.credentials['usernames']
	new_credentials = new_user_data.to_credentials_dict()

	if replace_username is not None:
		credentials.pop(replace_username)

	credentials[new_user_data.username] = new_credentials
	set_session_state_item('authenticator', authenticator)

	return authenticator


def edit_user_in_authenticator_object(username: str, new_user_data: User) -> Authenticate:
	"""
	Updates the authenticator object stored in the current session by editing the data of an existing user.

	:param username: The username of the user to be edited
	:param new_user_data: The new user data
	"""
	return add_new_user_to_authenticator_object(new_user_data, replace_username=username)


def remove_user_in_authenticator_object(username: str) -> Authenticate:
	"""
	Updates the authenticator object stored in the current session by removing a user.

	:param username: The username of the user to be removed
	"""
	authenticator: Authenticate = get_or_create_authenticator_object()
	credentials: dict = authenticator.authentication_controller.authentication_model.credentials['usernames']
	credentials.pop(username)
	set_session_state_item('authenticator', authenticator)
	return authenticator


def get_current_user_role() -> Role | None:
	"""Retrieves the role of the user if it is logged-in, otherwise it will return `None`."""
	role_str = get_session_state_item('roles')
	return Role.from_string(role_str)


def is_logged_in() -> bool:
	"""Check whether the user is logged in or not."""
	if get_session_state_item('authentication_status'):
		return True
	else:
		# Status is None or False
		return False


def create_new_user(new_first_name: str, new_last_name: str, new_email: str,
					new_username: str, new_password: str, new_password_repeat: str,
					captcha: bool = True, entered_captcha: Optional[str] = None,
					domains: Optional[List[str]] = None):
	"""
	Checks the validity of the form data and creates a new user in the database.

	:param new_first_name: The first name of the new user
	:param new_last_name: The last name of the new user
	:param new_email: The email of the new user
	:param new_username: The username of the new user
	:param new_password: The password of the new user
	:param new_password_repeat: The repeated password
	:param captcha: Whether the captcha input has been shown or not
	:param entered_captcha: The captcha entered by the user
	:param domains: The accepted domains for the registration, example: `domains=["gmail.com"]`
	:raises RegisterError If the data is not correct
	"""
	new_first_name = new_first_name.strip()
	new_last_name = new_last_name.strip()
	new_email = new_email.strip()
	new_username = new_username.lower().strip()
	new_password = new_password.strip()
	new_password_repeat = new_password_repeat.strip()

	# Data validation
	validator = Validator()

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

	# All data is correct
	new_user = User(
		first_name=new_first_name,
		last_name=new_last_name,
		username=new_username,
		password=User.hash_password(new_password),
		email=new_email,
		role=Role.NEW_USER.value,
	)

	# Push new user to database
	try:
		with get_db() as db:
			db.add(new_user)
			db.commit()
			db.refresh(new_user)

			print("New user created:", new_user)

			add_new_user_to_authenticator_object(new_user)
	except IntegrityError as e:
		message = str(e)
		if "users_username_key" in message:
			raise RegisterError('Username already exists')
		elif "users_email_key" in message:
			raise RegisterError('Email already exists')
		else:
			raise RegisterError('Unknown Integrity Error')
	except Exception as e:
		print(e)
		raise RegisterError('Unknown error')


def edit_username(old_username: str, new_username: str):
	"""
	Edits the username of a user in the database.

	:param old_username: The old username of the user to be edited
	:param new_username: The new username of the user to be edited
	:raises UpdateError If the data is not correct
	"""
	new_username = new_username.lower().strip()

	# Data validation
	validator = Validator()

	if old_username == new_username:
		raise UpdateError('New and current usernames are the same')

	if not validator.validate_username(new_username):
		raise UpdateError('Username is not valid')

	with get_db() as db:
		user = User.find_by(db, user_name=old_username)

		if user is None:
			raise UpdateError(f'User with username {old_username} does not exist')

		# All data is correct
		# Push changes to database
		try:
			user.username = new_username
			db.commit()
			db.refresh(user)

			print(f"Username updated (old={old_username}):", user)

			# Logout to remove cookie and set to it again after login
			authenticator = get_or_create_authenticator_object()
			authenticator.logout(location="unrendered")

			edit_user_in_authenticator_object(old_username, user)

		except IntegrityError as e:
			message = str(e)
			if "users_username_key" in message:
				raise UpdateError('Username already exists')
			else:
				raise UpdateError('Unknown Integrity Error')
		except Exception as e:
			print(e)
			raise UpdateError('Unknown error')


def edit_email(old_email: str, new_email: str):
	"""
	Edits the email of a user in the database
	:param old_email: The old email of the user to be edited
	:param new_email: The new email of the user to be edited
	:raises UpdateError If the data is not correct
	"""
	new_email = new_email.strip()

	# Data validation
	validator = Validator()

	if old_email == new_email:
		raise UpdateError('New and current emails are the same')

	if not validator.validate_email(new_email):
		raise RegisterError('Email is not valid')

	with get_db() as db:
		user = User.find_by(db, user_email=old_email)

		if user is None:
			raise UpdateError(f'User with email {old_email} does not exist')

		# All data is correct
		# Push changes to database
		try:
			user.email = new_email
			db.commit()
			db.refresh(user)

			print(f"Email updated (old={old_email}):", user)

			edit_user_in_authenticator_object(user.username, user)
		except IntegrityError as e:
			message = str(e)
			if "users_email_key" in message:
				raise UpdateError('Email already exists')
			else:
				raise UpdateError('Unknown Integrity Error')
		except Exception as e:
			print(e)
			raise UpdateError('Unknown error')


def edit_password(username: str, current_password: str, new_password: str, new_password_repeat: str):
	"""
	Edits the password of a user in the database.

	:param username: The username of the user to be edited
	:param current_password: The current password of the user to be edited
	:param new_password: The new password of the user to be edited
	:param new_password_repeat: The repeated new password
	:raises UpdateError If the data is not correct
	"""
	current_password = current_password.strip()
	new_password = new_password.strip()
	new_password_repeat = new_password_repeat.strip()

	# Data validation
	validator = Validator()

	if new_password != new_password_repeat:
		raise RegisterError('Passwords do not match')

	if not validator.validate_password(new_password):
		raise RegisterError('Password does not meet criteria')

	with get_db() as db:
		user = User.find_by(db, user_name=username)

		if user is None:
			raise UpdateError(f'User with username {username} does not exist')

		if not user.verify_password(current_password):
			raise RegisterError('Current password is incorrect')

		if user.verify_password(new_password):
			raise RegisterError('New and current passwords are the same')

		# All data is correct
		# Push changes to database
		try:
			user.password = User.hash_password(new_password)
			db.commit()
			db.refresh(user)

			print(f"Password updated for {username}:", user)

			edit_user_in_authenticator_object(username, user)
		except Exception as e:
			print(e)
			raise UpdateError('Unknown error')


def edit_first_last_name(username: str, new_first_name: str, new_last_name: str):
	"""
	Edits the email of a user in the database.

	:param username: The username of the user to be edited
	:param new_first_name: The new first name of the user to be edited, can be blank
	:param new_last_name: The new last name of the user to be edited, can be blank
	:raises UpdateError If the data is not correct
	"""
	new_first_name = new_first_name.strip()
	new_last_name = new_last_name.strip()

	# Data validation
	validator = Validator()

	if new_first_name == "" and new_last_name == "":
		raise RegisterError('First and last name cannot both be empty')

	if new_first_name != "" and not validator.validate_name(new_first_name):
		raise RegisterError('First name is not valid')

	if new_last_name != "" and not validator.validate_name(new_last_name):
		raise RegisterError('Last name is not valid')

	with get_db() as db:
		user = User.find_by(db, user_name=username)

		if user is None:
			raise UpdateError(f'User with username {username} does not exist')

		if new_first_name != "":
			if user.first_name == new_first_name:
				raise UpdateError('New and current first names are the same')
			else:
				user.first_name = new_first_name

		if new_last_name != "":
			if user.last_name == new_last_name:
				raise UpdateError('New and current last names are the same')
			else:
				user.last_name = new_last_name

		# All data is correct
		# Push changes to database
		try:
			db.commit()
			db.refresh(user)

			print(f"Name and surname updated for {username}:", user)

			edit_user_in_authenticator_object(username, user)

			return user.first_name, user.last_name
		except Exception as e:
			print(e)
			raise UpdateError('Unknown error')
