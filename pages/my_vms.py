import streamlit as st

from backend.roles import Roles
from frontend.page_options import page_setup

page_setup(title="My VMs", print_session_state=True, accepted_roles=[Roles.ADMIN, Roles.MANAGER, Roles.USER])

st.title("My VMs")
