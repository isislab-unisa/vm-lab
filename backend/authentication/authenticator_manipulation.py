from streamlit_authenticator import Authenticate

from backend.models import User
from backend.authentication.authenticator_creation import get_or_create_authenticator_object

from utils.session_state import set_session_state_item


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
