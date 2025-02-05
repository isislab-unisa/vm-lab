from frontend import page_setup, PageNames

################################
#            SETUP             #
################################

page_setup(
	title=PageNames.FORGOT_CREDENTIALS.label,
	access_control="unregistered_only",
)