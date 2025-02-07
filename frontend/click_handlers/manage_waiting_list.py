import streamlit as st
from streamlit import switch_page

from backend import Role, get_db, delete_from_db
from backend.models import User
from backend.authentication.authenticator_manipulation import remove_user_in_authenticator_object

from frontend import PageNames
from frontend.components import confirm_dialog, error_message
from frontend.forms.manage_waiting_list import new_user_accept_form


@st.dialog("Select role")
def new_user_accept_clicked_as_admin(data_row):
	user_to_accept: User = data_row["original_object"]
	return new_user_accept_form(
		user_to_accept=user_to_accept,
		available_roles_str=[
			# TODO: Add Regular user
			Role.to_phrase(Role.SIDEKICK),
			Role.to_phrase(Role.MANAGER)
		]
	)


@st.dialog("Select role")
def new_user_accept_clicked_as_manager(data_row):
	user_to_accept: User = data_row["original_object"]
	return new_user_accept_form(
		user_to_accept=user_to_accept,
		available_roles_str=[
			# TODO: Add Regular user
			Role.to_phrase(Role.SIDEKICK)
		]
	)


def new_user_denied_clicked(data_row):
	user_to_remove: User = data_row["original_object"]

	def new_user_deletion_process():
		try:
			with get_db() as db:
				delete_from_db(db, user_to_remove)

				remove_user_in_authenticator_object(user_to_remove.username)

				st.cache_data.clear()  # Refresh table data
				st.rerun()
		except Exception as e:
			error_message(unknown_exception=e)

	confirm_dialog(
		text="Are you sure you want to remove this new user?",
		caption="You cannot undo this action!",
		is_cancel_button_type_primary=True,
		confirm_button_callback=new_user_deletion_process
	)
