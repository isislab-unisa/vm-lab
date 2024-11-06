from backend.roles import Roles
from frontend.page_options import page_setup

page_setup(title="Manage Users", accepted_roles=[Roles.ADMIN, Roles.MANAGER])