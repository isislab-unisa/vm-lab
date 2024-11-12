import base64
from typing import Tuple, Optional

import paramiko
from paramiko.ssh_exception import AuthenticationException

from .session_state import pop_session_state, get_session_state, set_session_state

CREDENTIAL_KEYS = {
	"host": "vm_credentials_host",
	"port": "vm_credentials_port",
	"username": "vm_credentials_username",
	"password": "vm_credentials_password"
}

def clear_connection_credentials() -> None:
	"""Clears all connection credentials from the session state."""
	for key in CREDENTIAL_KEYS.values():
		pop_session_state(key)


def are_credentials_missing() -> bool:
	"""Checks if any connection credentials are missing from the session state."""
	for key in CREDENTIAL_KEYS.values():
		if get_session_state(key) is None:
			return True
	return False


def get_connection_credentials(clear_after_fetch: bool = True) -> Optional[Tuple[str, str, str, bytes]]:
	"""Retrieves connection credentials from the session state, optionally clearing them afterward."""
	if are_credentials_missing():
		return None

	host = get_session_state(CREDENTIAL_KEYS["host"])
	port = get_session_state(CREDENTIAL_KEYS["port"])
	username = get_session_state(CREDENTIAL_KEYS["username"])
	password = base64.b64encode(get_session_state(CREDENTIAL_KEYS["password"]).encode('utf-8'))

	if clear_after_fetch:
		clear_connection_credentials()

	return host, port, username, password


def test_connection(hostname: str, port: int, username: str, password: str, save_credentials: bool = True) -> None:
	"""Tests the SSH connection using provided credentials."""
	ssh_client = paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		ssh_client.connect(hostname=hostname, port=port, username=username, password=password)
		if save_credentials:
			set_session_state(CREDENTIAL_KEYS["host"], hostname)
			set_session_state(CREDENTIAL_KEYS["port"], port)
			set_session_state(CREDENTIAL_KEYS["username"], username)
			set_session_state(CREDENTIAL_KEYS["password"], password)
	except AuthenticationException:
		raise Exception("Authentication failed.")
	except Exception as ex:
		raise Exception("Connection failed:", str(ex))
	finally:
		ssh_client.close()
