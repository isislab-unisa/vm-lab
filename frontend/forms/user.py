import streamlit as st

from time import sleep
from streamlit import switch_page
from streamlit_authenticator import UpdateError

from backend import Role, get_db
from backend.authentication import edit_username, edit_email, edit_password, edit_first_last_name, edit_role
from backend.models import User

from frontend import PageNames
from frontend.components import error_message
from frontend.forms.authentication import PASSWORD_INSTRUCTIONS, USERNAME_INSTRUCTIONS

from utils.session_state import set_session_state_item, get_session_state_item, pop_session_state_item


def change_role_form(user: User, requesting_role: Role):
	if requesting_role == Role.ADMIN:
		available_roles = [Role.to_phrase(Role.SIDEKICK), Role.to_phrase(Role.MANAGER)]
	else:
		available_roles = [Role.to_phrase(Role.SIDEKICK)]

	index = 0
	match user.role:
		case Role.SIDEKICK.value:
			index = 0
		case Role.MANAGER.value:
			index = 1

	selected_role = st.selectbox(
		"Role",
		available_roles,
		index=index
	)

	if Role.from_phrase(selected_role).value == user.role:
		button = st.button("Change Role", type="primary", disabled=True)
	else:
		button = st.button("Change Role", type="primary")

	if get_session_state_item("role-change-success"):
		pop_session_state_item("role-change-success")
		st.success("Role changed successfully")

	if button:
		try:
			edit_role(user.username, Role.from_phrase(selected_role))

			set_session_state_item("selected_user", user)
			set_session_state_item("role-change-success", True)

			st.cache_data.clear() # Refresh table data
			st.rerun()
		except UpdateError as e:
			error_message(cause=str(e))
		except Exception as e:
			error_message(unknown_exception=e)


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
				switch_page(PageNames.LOGIN())
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
				switch_page(PageNames.USER_SETTINGS())
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
				switch_page(PageNames.USER_SETTINGS())
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
				switch_page(PageNames.USER_SETTINGS())
			except Exception as e:
				st.error(e)