# Modified code from streamlit_authenticator\views\authentication_view.py (Authenticate.register_user)
from typing import Optional, List

import streamlit as st
from streamlit import switch_page
from streamlit_authenticator.utilities import Helpers

from backend.authentication import create_new_user, edit_username, get_or_create_authenticator_object
from frontend.page_names import PageNames
from utils.session_state import set_session_state, get_session_state, pop_session_state


def register_user(key: str = 'Register user', domains: Optional[List[str]] = None, captcha: bool = True):
	"""
	Renders a form for user registration
	:param key: (optional) The key of the form
	:param domains: (optional) The accepted domains for the registration, example: `domains=["gmail.com"]`
	:param captcha: (optional) Whether to show the captcha input or not
	:raises RegisterError If the data is not correct
	"""
	with st.form(key):
		st.subheader('Register user')

		col1_1, col2_1 = st.columns(2)

		new_first_name = col1_1.text_input('First name')
		new_last_name = col1_1.text_input('Last name')
		new_email = col2_1.text_input('Email')

		username_instructions = """
				**Username must be:**
				- Between 1 and 20 characters long.
				- Lowercase.
				"""
		new_username = col2_1.text_input('Username', help=username_instructions)

		col1_2, col2_2 = st.columns(2)

		password_instructions = """
				**Password must be:**
				- Between 8 and 20 characters long.
				- Contain at least one lowercase letter.
				- Contain at least one uppercase letter.
				- Contain at least one digit.
				- Contain at least one special character from [@$!%*?&].
				"""
		new_password = col1_2.text_input('Password', type='password', help=password_instructions)
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
			set_session_state('registration-success', True)
			switch_page(PageNames.login)


def change_username(current_username: str, key: str = 'Change username'):
	with st.form(key):
		st.subheader('Change username')
		st.write(f"Current username: `{current_username}`")

		username_instructions = """
				**Username must be:**
				- Between 1 and 20 characters long.
				- Lowercase.
				"""
		new_username = st.text_input('New username', help=username_instructions)

		submitted = st.form_submit_button('Change username', type='primary')

		if get_session_state('username-change-success'):
			pop_session_state('username-change-success')
			st.success(f"Username changed successfully to `{new_username}`")

		if submitted:
			try:
				edit_username(current_username, new_username)
				set_session_state('username', new_username)
				set_session_state('username-change-success', True)
				switch_page(PageNames.user_settings)
			except Exception as e:
				st.error(e)

