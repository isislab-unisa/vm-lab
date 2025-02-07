import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate

from backend import get_db
from backend.models import User
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


def get_or_create_authenticator_object(force_create: bool = False) -> Authenticate:
	"""Returns the streamlit-authenticator object in the session state, or creates and returns a new one if it wasn't found."""
	authenticator = get_session_state_item('authenticator')

	if authenticator is None or force_create:
		authenticator = create_authenticator_object()

	return authenticator


