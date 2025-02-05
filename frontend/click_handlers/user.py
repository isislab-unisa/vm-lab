from streamlit import switch_page

from backend.models import User
from frontend import PageNames
from utils.session_state import set_session_state_item


def user_details_clicked(data_row):
	callback_user: User = data_row["original_object"]
	set_session_state_item("selected_user", callback_user)
	switch_page(PageNames.DETAILS_USER())
