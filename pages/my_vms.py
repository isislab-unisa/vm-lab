import streamlit as st

from backend.roles import Roles
from frontend.page_options import page_setup, AccessControlType

authenticator = page_setup(
	title="My VMs",
	access_control=AccessControlType.ACCEPTED_ROLES_ONLY,
	accepted_roles=[Roles.ADMIN, Roles.MANAGER, Roles.USER],
	print_session_state=True
)

st.title("My VMs")
