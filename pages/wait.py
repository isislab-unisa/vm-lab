import streamlit as st

from backend.role import Role
from frontend.page_names import PageNames
from frontend.page_setup import page_setup

page_setup(
	title='Waiting List',
	access_control="accepted_roles_only",
	accepted_roles=[Role.NEW_USER],
	new_user_redirect_to_wait_page=False,
	role_not_accepted_redirect=PageNames.MAIN_DASHBOARD,
)

st.title("You are on a waiting list")
st.write("Return later, after your account has been approved.")