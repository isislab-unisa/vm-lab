# THIS FILE CONTAINS SOME EDITED CODE
# FROM `streamlit_authenticator\views\authentication_view.py`
#
# (Authenticate.register_user)
import streamlit as st

from time import sleep
from typing import Optional, List
from streamlit import switch_page
from streamlit_authenticator.utilities import Helpers

from backend.authentication import create_new_user, edit_username, edit_email, edit_password, edit_first_last_name
from frontend.page_names import PageNames
from utils.session_state import set_session_state_item, get_session_state_item, pop_session_state_item

PASSWORD_INSTRUCTIONS = """
		**Password must be:**
		- Between 8 and 20 characters long.
		- Contain at least one lowercase letter.
		- Contain at least one uppercase letter.
		- Contain at least one digit.
		- Contain at least one special character from [@$!%*?&].
		"""

USERNAME_INSTRUCTIONS = """
		**Username must be:**
		- Between 1 and 20 characters long.
		- Lowercase.
		"""


def register_user(key: str = 'Register user', clear_on_submit: bool = False, domains: Optional[List[str]] = None,
				  captcha: bool = True):
	"""
	Renders a form for user registration.

	:param clear_on_submit: Whether to clear the inserted data in the form after submit
	:param key: The key of the form (must be different from other forms on the same page)
	:param domains: The accepted domains for the registration, example: `domains=["gmail.com"]`
	:param captcha: Whether to show the captcha input or not
	:raises RegisterError If the data is not correct
	"""
	with st.form(key=key, clear_on_submit=clear_on_submit):
		st.subheader('Register user')

		col1_1, col2_1 = st.columns(2)

		new_first_name = col1_1.text_input('First name')
		new_last_name = col1_1.text_input('Last name')
		new_email = col2_1.text_input('Email')
		new_username = col2_1.text_input('Username', help=USERNAME_INSTRUCTIONS)

		col1_2, col2_2 = st.columns(2)

		new_password = col1_2.text_input('Password', type='password', help=PASSWORD_INSTRUCTIONS)
		new_password_repeat = col2_2.text_input('Repeat password', type='password')

		entered_captcha = None
		if captcha:
			entered_captcha = st.text_input('Captcha').strip()
			st.image(Helpers.generate_captcha('register_user_captcha'))

		submitted = st.form_submit_button('Register', type='primary')

		if submitted:
			create_new_user(
				new_first_name=new_first_name,
				new_last_name=new_last_name,
				new_email=new_email,
				new_username=new_username,
				new_password=new_password,
				new_password_repeat=new_password_repeat,
				entered_captcha=entered_captcha,
				domains=domains
			)
			# Switch page if there is no error with the registration
			set_session_state_item('registration-success', True)
			switch_page(PageNames.login)


def change_username(current_username: str, clear_on_submit: bool = False, key: str = 'Change username'):
	"""
	Renders a form for username change.

	:param current_username: The current username
	:param clear_on_submit: Whether to clear the inserted data in the form after submit
	:param key: The key of the form (must be different from other forms on the same page)
	"""
	with st.form(key=key, clear_on_submit=clear_on_submit):
		st.subheader('Change username')
		st.write(f"Current username: `{current_username}`")

		new_username = st.text_input('New username', help=USERNAME_INSTRUCTIONS)
		st.warning("After submitting, you will be logged out and the new username can be used to log back in")

		submitted = st.form_submit_button('Change username', type='primary')

		if submitted:
			try:
				edit_username(current_username, new_username)
				set_session_state_item('username-change-success', True)
				sleep(0.2)  # Wait to let the login cookie deletion happen during logout
				switch_page(PageNames.login)
			except Exception as e:
				st.error(e)


def change_email(current_email: str, clear_on_submit: bool = False, key: str = 'Change email'):
	"""
	Renders a form for email change.

	:param current_email: The current email
	:param clear_on_submit: Whether to clear the inserted data in the form after submit
	:param key: The key of the form (must be different from other forms on the same page)
	"""
	with st.form(key=key, clear_on_submit=clear_on_submit):
		st.subheader('Change email')
		st.write(f"Current email: `{current_email}`")

		new_email = st.text_input('New email')

		submitted = st.form_submit_button('Change email', type='primary')

		if get_session_state_item('email-change-success'):
			pop_session_state_item('email-change-success')
			st.success(f"Email changed successfully to `{new_email}`")

		if submitted:
			try:
				edit_email(current_email, new_email)
				set_session_state_item('email', new_email)
				set_session_state_item('email-change-success', True)
				switch_page(PageNames.user_settings)
			except Exception as e:
				st.error(e)


def change_password(current_username: str, clear_on_submit: bool = False, key: str = 'Change password'):
	"""
	Renders a form for password change.

	:param current_username: The current username
	:param clear_on_submit: Whether to clear the inserted data in the form after submit
	:param key: The key of the form (must be different from other forms on the same page)
	"""
	with st.form(key=key, clear_on_submit=clear_on_submit):
		st.subheader('Change password')

		current_password = st.text_input('Current password', type='password')
		new_password = st.text_input('New password', type='password', help=PASSWORD_INSTRUCTIONS)
		new_password_repeat = st.text_input('Repeat password', type='password')

		submitted = st.form_submit_button('Change password', type='primary')

		if get_session_state_item('password-change-success'):
			pop_session_state_item('password-change-success')
			st.success(f"Password changed successfully")

		if submitted:
			try:
				edit_password(current_username, current_password, new_password, new_password_repeat)
				set_session_state_item('password-change-success', True)
				switch_page(PageNames.user_settings)
			except Exception as e:
				st.error(e)


def change_first_last_name(current_username: str, current_name_surname: str, clear_on_submit: bool = False,
						   key: str = 'Change name surname'):
	"""
	Renders a form for email change.

	:param current_username: The current username
	:param current_name_surname: The current name and surname from the session_state
	:param clear_on_submit: Whether to clear the inserted data in the form after submit
	:param key: The key of the form (must be different from other forms on the same page)
	"""
	with st.form(key=key, clear_on_submit=clear_on_submit):
		st.subheader('Change name and surname')
		st.write(f"Current name and surname: `{current_name_surname}`, leave a field blank to not change it")

		new_first_name = st.text_input('New first name')
		new_last_name = st.text_input('New last name')

		submitted = st.form_submit_button('Change name and surname', type='primary')

		if get_session_state_item('name-surname-change-success'):
			pop_session_state_item('name-surname-success')

			if new_first_name == "" and new_last_name == "":
				pass
			elif new_first_name == "":
				st.success(f"Last name changed successfully to `{new_last_name}`")
			elif new_last_name == "":
				st.success(f"First name changed successfully to `{new_first_name}`")
			else:
				st.success(f"First name and last name changed successfully to `{new_first_name} {new_last_name}`")

		if submitted:
			try:
				edited_first_name, edited_last_name = edit_first_last_name(current_username, new_first_name,
																		   new_last_name)
				set_session_state_item('name', f'{edited_first_name} {edited_last_name}')
				set_session_state_item('name-surname-change-success', True)
				switch_page(PageNames.user_settings)
			except Exception as e:
				st.error(e)