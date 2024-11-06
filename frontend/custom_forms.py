# Modified code from streamlit_authenticator\views\authentication_view.py (Authenticate.register_user)
from typing import Optional, List, Dict, Callable

import streamlit as st
from streamlit_authenticator.utilities import Helpers

from backend.authentication import register_new_user
from utils.session_state import set_session_state


def register_user(key: str='Register user', domains: Optional[List[str]]=None, captcha: bool=True):
	with st.form(key):
		st.subheader('Register user')

		col1_1, col2_1 = st.columns(2)

		new_first_name = col1_1.text_input('First name')
		new_last_name = col2_1.text_input('Last name')
		new_email = col1_1.text_input('Email')
		new_username = col2_1.text_input('Username')

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
			print("Submitted:", new_first_name, new_last_name, new_email, new_username, new_password,
				  new_password_repeat, entered_captcha)
			register_new_user(
				new_first_name=new_first_name,
				new_last_name=new_last_name,
				new_email=new_email,
				new_username=new_username,
				new_password=new_password,
				new_password_repeat=new_password_repeat,
				entered_captcha=entered_captcha,
				domains=domains
			)
			set_session_state('registration_success', True)
