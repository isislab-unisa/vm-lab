import streamlit as st

from backend.role import Role
from frontend.page_options import page_setup, AccessControlType

authenticator = page_setup(
	title="Terminal",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER, Role.USER],
	print_session_state=True
)

st.title("Terminal")
