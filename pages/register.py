import streamlit as st

from frontend import page_setup, PageNames
from frontend.forms.registration import register_user_form


################################
#            SETUP             #
################################

page_setup(
	title=PageNames.REGISTER.label,
	access_control="unregistered_only",
)


################################
#             PAGE             #
################################

try:
	# TODO: limit the registration attempts to 5-6 captcha errors
	register_user_form(captcha=False)
except Exception as e:
	st.error(e)