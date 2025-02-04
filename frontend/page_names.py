class PageNames:
	"""This is not an enum to reduce the amount of `.value`s to write"""
	ERROR = "pages/error.py"							# all
	YOU_ARE_IN_WAITING_LIST = "pages/wait.py"								# NEW_USER

	REGISTER = "pages/register.py"						# unregistered
	LOGIN = "pages/login.py"							# unregistered
	LOGOUT = "pages/logout.py"							# registered
	FORGOT_CREDENTIALS = "pages/forgot_credentials.py"	# unregistered

	MAIN_DASHBOARD = "pages/my_vms.py"							# ADMIN, MANAGER, USER

	USER_SETTINGS = "pages/user_settings.py"			# registered
	VM_CONNECTION = "pages/terminal.py"						# ADMIN, MANAGER, USER

	MANAGE_USER_LIST = "pages/manage_users.py"				# ADMIN, MANAGER
	MANAGE_WAITING_LIST = "pages/new_users_waiting_list.py"	# ADMIN, MANAGER

	DETAILS_VM = "pages/vm_details.py"  # ADMIN, MANAGER, USER
	DETAILS_USER = "pages/user_details.py"				# ADMIN, MANAGER
