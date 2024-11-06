from streamlit import switch_page

from backend.authentication import is_logged_in
from backend.roles import Roles
from frontend.page_names import PageNames
from frontend.page_options import page_setup

page_setup(title="Terminal", accepted_roles=[Roles.ADMIN, Roles.MANAGER, Roles.USER])

