from streamlit import switch_page

from backend.authentication import get_authenticator_object, is_logged_in
from frontend.page_names import PageNames
from frontend.page_options import page_setup

page_setup()

if is_logged_in():
    get_authenticator_object().logout(location="unrendered")
else:
    switch_page(PageNames.login)