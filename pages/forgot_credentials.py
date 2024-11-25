from frontend.page_options import page_setup, AccessControlType

page_setup(
	title="Forgot Credentials",
	access_control=AccessControlType.UNREGISTERED_ONLY,
)