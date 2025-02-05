class PageEntry:
	def __init__(self, file_name, label):
		self.file_name = file_name
		self.label = label

	def __str__(self):
		return self.file_name

	def __call__(self):
		return self.file_name


class PageNames:
	"""
	Class that holds all the pages file names and labels for the application.

	- To get the file name, call the page as a function (e.g. `PageNames.ERROR()`) or use the `file_name` attribute.
	- To get the label, use the `label` attribute.
	"""
	ERROR = PageEntry(
		"pages/error.py",
		"Error"
	)
	YOU_ARE_IN_WAITING_LIST = PageEntry(
		"pages/wait.py",
		"You are in the Waiting List"
	)

	REGISTER = PageEntry(
		"pages/register.py",
		"Register"
	)
	LOGIN = PageEntry(
		"pages/login.py",
		"Login"
	)
	LOGOUT = PageEntry(
		"pages/logout.py",
		"Logout"
	)
	FORGOT_CREDENTIALS = PageEntry(
		"pages/forgot_credentials.py",
		"Forgot Credentials"
	)

	MAIN_DASHBOARD = PageEntry(
		"pages/my_vms.py",
		"My Dashboard")

	USER_SETTINGS = PageEntry(
		"pages/user_settings.py",
		"Settings"
	)
	VM_CONNECTION = PageEntry(
		"pages/terminal.py",
		"VM Connection"
	)

	MANAGE_USER_LIST = PageEntry(
		"pages/manage_users.py",
		"Manage Users"
	)
	MANAGE_WAITING_LIST = PageEntry(
		"pages/new_users_waiting_list.py",
		"Manage Waiting List"
	)

	DETAILS_VM = PageEntry(
		"pages/vm_details.py",
		"VM Details"
	)
	DETAILS_USER = PageEntry(
		"pages/user_details.py",
		"User Details"
	)
