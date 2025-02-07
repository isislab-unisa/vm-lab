import streamlit as st

from backend.database import get_db, delete_from_db
from backend.models import Bookmark
from frontend.components import error_toast, confirm_dialog
from frontend.forms.bookmark import bookmark_add_form, bookmark_edit_form


@st.dialog("Add Bookmark")
def bookmark_add_clicked(current_username: str):
	return bookmark_add_form(current_username)


@st.dialog("Edit Bookmark")
def bookmark_edit_clicked(data_row):
	bookmark: Bookmark = data_row["original_object"]
	return bookmark_edit_form(bookmark)


def bookmark_delete_clicked(data_row):
	bookmark: Bookmark = data_row["original_object"]

	def bookmark_deletion_process():
		with get_db() as db:
			try:
				delete_from_db(db, bookmark)
			except Exception as e:
				error_toast(unknown_exception=e)
			else:
				st.cache_data.clear()  # Refresh tables
				st.rerun()

	confirm_dialog(
		text=f"Are you sure you want to delete `{bookmark.name}`?",
		confirm_button_callback=bookmark_deletion_process
	)