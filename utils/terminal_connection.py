import io
import paramiko
import requests

from typing import Dict
from paramiko.ssh_exception import AuthenticationException


def test_connection(hostname: str, port: int, username: str,
					password: str = None, ssh_key: bytes = None,
					terminal_url: str = "http://localhost:8888",
					sftp_url: str = "http://localhost:8261"):
	"""
	Tests the SSH connection using provided credentials and returns the url to the browser terminal.

	:return: The json response as a dict, can contain "url" or "error"
	:raises AuthenticationException: If the credentials are incorrect
	:raises Exception: Other connection issues
	"""
	ssh_client = paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		if ssh_key:
			# Test the connection with the key

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

			private_key = load_private_key(ssh_key.decode("utf-8"))

			ssh_client.connect(
				hostname=hostname,
				port=port,
				username=username,
				pkey=private_key
			)

			# If the connection is successful
			response_ssh = requests.post(
				url=f"{terminal_url}/create-session",
				data={
					"hostname": hostname,
					"username": username,
					"port": port,
				},
				files={
					"ssh_key": ssh_key # Send as bytes
				}
			)

			response_sftp = requests.post(
				url=f"{sftp_url}/api/sftp/credentials/create",
				json={
					"name": f"{username}@{hostname}:{port}",
					"host": hostname,
					"username": username,
					"port": port,
					"privateKey": ssh_key.decode("utf-8") # Send as text
				}
			)

			return response_ssh.json(), response_sftp.json()
		elif password:
			# Test the connection with the password
			ssh_client.connect(
				hostname=hostname,
				port=port,
				username=username,
				password=password
			)

			# If the connection is successful
			response_ssh = requests.post(
				url=f"{terminal_url}/create-session",
				json={
					"hostname": hostname,
					"username": username,
					"port": port,
					"password": password,
				},
			)

			response_sftp = requests.post(
				url=f"{sftp_url}/api/sftp/credentials/create",
				json={
					"name": f"{username}@{hostname}:{port}",
					"host": hostname,
					"username": username,
					"port": port,
					"password": password,
				},
			)

			return response_ssh.json(), response_sftp.json()
		else:
			raise ValueError("No password or SSH key provided.")
	except AuthenticationException:
		raise Exception("Authentication failed.")
	except Exception as e:
		raise Exception("Connection failed:", str(e))
	finally:
		# Close the testing connection
		ssh_client.close()
