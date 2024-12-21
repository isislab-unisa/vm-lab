# THIS FILE CONTAINS SOME EDITED CODE
# FROM `streamlit_authenticator\views\authentication_view.py`
#
# (Authenticate.register_user)
from typing import Optional, List

import streamlit as st
from streamlit import switch_page
from streamlit_authenticator.utilities import Helpers

from backend.authentication import create_new_user
from frontend.page_names import PageNames
from utils.session_state import set_session_state_item

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
