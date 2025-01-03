import streamlit as st

from backend.role import Role
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType

page_setup(
	title='Waiting List',
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.NEW_USER],
	new_user_redirect_to_wait_page=False,
	role_not_accepted_redirect=PageNames.my_vms,
)

st.title("You are on a waiting list")
st.write("Return later, after your account has been approved.")