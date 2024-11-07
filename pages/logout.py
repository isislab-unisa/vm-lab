from frontend.page_options import page_setup, AccessControlType

authenticator = page_setup(
    title="Logout",
    access_control=AccessControlType.LOGGED_IN_ONLY,
)

authenticator.logout(location="unrendered")
