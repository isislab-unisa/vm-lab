import io
import paramiko
import requests
import streamlit as st

from typing import Literal
from paramiko.ssh_exception import AuthenticationException


def build_module_url(connection_type: Literal["ssh", "sftp"],
					 request_type: Literal["credentials", "connection"],
					 connection_id = None):
	"""Builds a string to use as URL for the connection with an ID."""
	url_format: str = st.secrets[f'{connection_type}_{request_type}_request_format']

	if connection_type == "ssh":
		url_format = (url_format
					  .replace("$SSH_URL", st.secrets["ssh_module_url"])
					  .replace("$SSH_PORT", st.secrets["ssh_module_port"]))
	else:
		url_format = (url_format
					  .replace("$SFTP_URL", st.secrets["sftp_module_url"])
					  .replace("$SFTP_PORT", st.secrets["sftp_module_port"]))

	if request_type == "connection" and connection_id:
		return url_format.replace("$CONNECTION_ID", connection_id)
	else:
		return url_format


def load_private_key(key_str):
	"""
	Automatically identifies the type of ssh key.
	"""
	key_file = io.StringIO(key_str)
	for key_class in (paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey, paramiko.Ed25519Key):
		try:
			return key_class.from_private_key(key_file)
		except paramiko.SSHException:
			key_file.seek(0)  # Reset the ssh key pointer position to try with another type
	raise ValueError("Key format not valid (RSA, DSS, ECDSA, ED25519).")


def test_connection_with_paramiko(hostname: str, port: int, username: str,
								  password: str = None, ssh_key: bytes = None):
	ssh_client = paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	if ssh_key:
		private_key = load_private_key(ssh_key.decode("utf-8"))
		ssh_client.connect(
			hostname=hostname,
			port=port,
			username=username,
			pkey=private_key
		)
	elif password:
		ssh_client.connect(
			hostname=hostname,
			port=port,
			username=username,
			password=password
		)
	else:
		ssh_client.close()
		raise ValueError("No ssh key or password provided.")

	ssh_client.close()



def send_credentials_to_external_module(module_type: Literal["ssh", "sftp"],
										hostname: str, port: int, username: str,
										password: str = None, ssh_key: bytes = None):
	"""
	Tests the SSH connection using provided credentials and returns the url to the browser terminal.

	:return: The json response as a dict, can contain "url" or "error"
	:raises AuthenticationException: If the credentials are incorrect
	:raises Exception: Other connection issues
	"""
	module_url = build_module_url(
		connection_type=module_type,
		request_type="credentials",
	)

	module_response = None

	# Make the correct request body
	if ssh_key:
		if module_type == "ssh":
			module_response = requests.post(
				url=module_url,
				data={
					"hostname": hostname,
					"username": username,
					"port": port,
				},
				files={
					"ssh_key": ssh_key # Send as bytes
				}
			)
		elif module_type == "sftp":
			module_response = requests.post(
				url=module_url,
				json={
					"name": f"{username}@{hostname}:{port}",
					"host": hostname,
					"username": username,
					"port": port,
					"privateKey": ssh_key.decode("utf-8") # Send as text
				}
			)
	elif password:
		if module_type == "ssh":
			module_response = requests.post(
				url=module_url,
				json={
					"hostname": hostname,
					"username": username,
					"port": port,
					"password": password,
				},
			)
		elif module_type == "sftp":
			module_response = requests.post(
				url=module_url,
				json={
					"name": f"{username}@{hostname}:{port}",
					"host": hostname,
					"username": username,
					"port": port,
					"password": password,
				},
			)
	else:
		raise ValueError("No password or SSH key provided.")

	if module_response is not None:
		return module_response.json()
	else:
		raise Exception(f"No request was sent to the {module_type} module.")
