import streamlit as st

from backend import add_to_db
from backend.database import get_db
from backend.models import Bookmark, User
from frontend.components import error_message


def bookmark_add_form(current_username: str):
	with st.form(f"add-bookmark-form"):
		name = st.text_input("Bookmark name", placeholder="Insert name")
		link = st.text_input("Link", placeholder="Insert link", help="Must start with `www.`")
		submit_button = st.form_submit_button("Save")

	if submit_button:
		if not name or not link:
			st.warning("Fill out all of the required fields.")
		elif not link.startswith("www."):
			st.error("Insert a valid link")
		else:
			try:
				with get_db() as db:
					new_bookmark = Bookmark(
						name=name,
						link=link,
					)
					user = User.find_by_user_name(db, current_username)
					new_bookmark.user_id = user.id

					add_to_db(db, new_bookmark)
			except Exception as e:
				error_message(unknown_exception=e)
			else:
				st.cache_data.clear()  # Refresh table
				st.rerun()


def bookmark_edit_form(bookmark: Bookmark):
	with st.form(f"edit-form-bookmark-{bookmark.id}"):
		name = st.text_input("VM name", value=bookmark.name, placeholder="Insert name")
		link = st.text_input("Link", value=bookmark.link, placeholder="Insert link")
		submit_button = st.form_submit_button("Edit", type="primary")

	if submit_button:
		with get_db() as db:
			try:
				bookmark = Bookmark.find_by_id(db, bookmark.id)
				bookmark.name = name
				bookmark.link = link
				db.commit()
			except Exception as e:
				error_message(unknown_exception=e)
			else:
				st.cache_data.clear()  # Refresh table
				st.rerun()