from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from streamlit_authenticator import RegisterError, UpdateError
from streamlit_authenticator.utilities import Validator, Helpers

from backend import Role, get_db, add_to_db, delete_from_db
from backend.models import User, VirtualMachine, Bookmark
from backend.authentication.authenticator_creation import get_or_create_authenticator_object
from backend.authentication.authenticator_manipulation import add_new_user_to_authenticator_object, \
	edit_user_in_authenticator_object, remove_user_in_authenticator_object


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
			new_user = add_to_db(db, new_user)

			add_new_user_to_authenticator_object(new_user)
	except IntegrityError as e:
		message = str(e)
		if "users_username_key" in message:
			raise RegisterError('Username already exists')
		elif "users_email_key" in message:
			raise RegisterError('Email already exists')
		else:
			raise RegisterError(message)
	except Exception as e:
		raise RegisterError(str(e))


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
		user = User.find_by_user_name(db, old_username)

		if user is None:
			raise UpdateError(f'User with username {old_username} does not exist')

		# All data is correct
		# Push changes to database
		try:
			user.username = new_username
			db.commit()
			db.refresh(user)

			# Logout to remove cookie and set to it again after login
			authenticator = get_or_create_authenticator_object()
			authenticator.logout(location="unrendered")

			edit_user_in_authenticator_object(old_username, user)

		except IntegrityError as e:
			message = str(e)
			if "users_username_key" in message:
				raise UpdateError('Username already exists')
			else:
				raise UpdateError(message)
		except Exception as e:
			raise UpdateError(str(e))


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
		user = User.find_by_email(db, old_email)

		if user is None:
			raise UpdateError(f'User with email {old_email} does not exist')

		# All data is correct
		# Push changes to database
		try:
			user.email = new_email
			db.commit()
			db.refresh(user)

			edit_user_in_authenticator_object(user.username, user)
		except IntegrityError as e:
			message = str(e)
			if "users_email_key" in message:
				raise UpdateError('Email already exists')
			else:
				raise UpdateError(message)
		except Exception as e:
			raise UpdateError(str(e))


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
		user = User.find_by_user_name(db, username)

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

			edit_user_in_authenticator_object(username, user)
		except Exception as e:
			raise UpdateError(str(e))


def edit_first_last_name(username: str, new_first_name: str, new_last_name: str):
	"""
	Edits the email of a user in the database.

	:param username: The username of the user to be edited
	:param new_first_name: The new first name of the user to be edited, can be blank
	:param new_last_name: The new last name of the user to be edited, can be blank
	:raises UpdateError If the data is not correct
	:return: The new first and last name
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
		user = User.find_by_user_name(db, username)

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

			edit_user_in_authenticator_object(username, user)

			return user.first_name, user.last_name
		except Exception as e:
			raise UpdateError(str(e))


def edit_role(username: str, new_role: Role):
	"""
	Edits the role of a user in the database.

	:param username: The username of the user to be edited
	:param new_role: The new role of the user to be edited
	:raises UpdateError If the data is not correct
	"""
	with get_db() as db:
		user = User.find_by_user_name(db, username)

		if user is None:
			raise UpdateError(f'User with username {username} does not exist')

		user.role = new_role.value

		# All data is correct
		# Push changes to database
		db.commit()
		db.refresh(user)

		edit_user_in_authenticator_object(username, user)


def disable_user(username: str, revert: bool = False):
	"""
	Disables a user by removing it from in the authenticator.
	:param username: The username of the user to be disabled
	:raises UpdateError If the user has not been found
	"""
	with get_db() as db:
		user = User.find_by_user_name(db, username)

		if user is None:
			raise UpdateError(f'User with username {username} does not exist')

		user.disabled = not revert
		db.commit()
		db.refresh(user)

		remove_user_in_authenticator_object(username)


def delete_user(username: str):
	"""
	Deletes a user from the database.
	:param username: The username of the user to be deleted
	:raises UpdateError If the user has not been found
	"""
	with get_db() as db:
		user = User.find_by_user_name(db, username)

		if user is None:
			raise UpdateError(f'User with username {username} does not exist')

		# Delete VMs
		user_vms = VirtualMachine.find_by_user_name(db, user.username)
		for vm in user_vms:
			delete_from_db(db, vm)

		# Delete Bookmarks
		user_bookmarks = Bookmark.find_by_user_name(db, user.username)
		for bookmark in user_bookmarks:
			delete_from_db(db, bookmark)

		# Delete User
		delete_from_db(db, user)

		remove_user_in_authenticator_object(username)
