import streamlit as st

from backend.role import Role
from frontend.page_names import PageNames
from frontend.page_options import page_setup, AccessControlType

authenticator = page_setup(
	title="Manage Users",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Role.ADMIN, Role.MANAGER],
	role_not_accepted_redirect=PageNames.my_vms,
	print_session_state=True
)

st.title("Manage Users")