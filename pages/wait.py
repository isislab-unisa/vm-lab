import streamlit as st

from backend import Role

from frontend import PageNames, page_setup


page_setup(
	title=PageNames.YOU_ARE_IN_WAITING_LIST.label,
	access_control="accepted_roles_only",
	accepted_roles=[Role.NEW_USER],
	new_user_redirect_to_wait_page=False,
	role_not_accepted_redirect=PageNames.MAIN_DASHBOARD,
)

st.title(PageNames.YOU_ARE_IN_WAITING_LIST.label)
st.write("Return later, after your account has been approved.")