from typing import Literal

import streamlit as st

from backend import get_db
from backend.models import VirtualMachine, Bookmark
from frontend.components import error_message


@st.cache_data
def get_vm_data_from_db(username: str,
						scope: Literal["my_owned_vms", "my_assigned_vms", "all_owned_vms", "all_assigned_vms"],
						shared: bool = None):
	"""
	Fetch VM data from the database.

	:param scope: Whether to get the VMs for the current user ("this_user") or all users except for the current user ("all_users").
	:return: List of dictionaries with VM info.
	"""
	try:
		with get_db() as db:
			if scope == "my_owned_vms":
				vm_list = VirtualMachine.find_by_user_name(db, username, exclude_assigned_to=True, shared=shared)
			elif scope == "my_assigned_vms":
				vm_list = VirtualMachine.find_by_assigned_to(db, username)
			elif scope == "all_owned_vms":
				vm_list = VirtualMachine.find_all(db, shared=True, assigned_to=False, exclude_user_name=username)
			elif scope == "all_assigned_vms":
				vm_list = VirtualMachine.find_all(db, assigned_to=True)
			else:
				raise ValueError(f"Invalid vm search scope.")

		result = []
		for vm in vm_list:
			result.append(build_vm_dict(vm, username))

		return result
	except ValueError as e:
		error_message(cause=str(e))
	except Exception as e:
		error_message(unknown_exception=e)


def build_vm_dict(vm: VirtualMachine, requesting_user_name: str):
	"""Build a correct dictionary with the VM info to display in the table."""
	if vm.ssh_key:
		auth_type = ":material/key: SSH Key"
	elif vm.password:
		auth_type = ":material/password: Password"
	else:
		auth_type = ":material/do_not_disturb_on: None"

	try:
		owner = vm.user.username
	except KeyError:
		raise KeyError(f"Could not find the owner of the VM `{vm.name}`.")

	vm_dict = {
		# Hidden
		"original_object": vm,
		"requesting_user": requesting_user_name,
		# Shown in columns
		"name": vm.name,
		"host_complete": f":blue[{vm.host}] : :red[{vm.port}]",
		"username": vm.username,
		"shared": ":heavy_check_mark: Yes" if vm.shared else ":x: No",
		"auth": auth_type,
		"owner": owner,
		"assigned_to": vm.assigned_to,
		# Button disabled settings
		"buttons_disabled": {}
	}

	return vm_dict


@st.cache_data
def get_bookmark_data_from_db(requesting_user_name: str):
	with get_db() as db_bookmark_list:
		bookmark_list = Bookmark.find_by_user_name(db_bookmark_list, requesting_user_name)

	result = []
	for bookmark in bookmark_list:
		bookmark_dict = {
			# Hidden
			"original_object": bookmark,
			# Shown in columns
			"name": bookmark.name,
			"url": bookmark.link,
			# Button disabled settings
			"buttons_disabled": {}
		}
		result.append(bookmark_dict)

	return result
