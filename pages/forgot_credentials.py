from frontend.page_options import page_setup, AccessControlType

authenticator = page_setup(
	title="Forgot Credentials",
	access_control=AccessControlType.UNREGISTERED_ONLY,
	print_session_state=True
)