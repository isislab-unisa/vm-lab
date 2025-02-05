import streamlit as st
from streamlit_authenticator import UpdateError

from backend import Role
from backend.models import User
from backend.authentication import edit_role

from frontend.components import error_message


def new_user_accept_form(user_to_accept: User, available_roles_str: list[str]):
	selection = st.selectbox(
		"Role",
		available_roles_str,
	)

	if st.button("Add", type="primary"):
		selected_role = Role.from_phrase(selection)

		try:
			edit_role(user_to_accept.username, selected_role)

			st.cache_data.clear() # Refresh table data
			st.rerun()
		except UpdateError as e:
			error_message(cause=str(e))
		except Exception as e:
			error_message(unknown_exception=e)