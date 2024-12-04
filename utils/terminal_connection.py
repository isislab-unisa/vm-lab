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
			ssh_client.connect(
				hostname=hostname,
				port=port,
				username=username,
				pkey=paramiko.RSAKey.from_private_key(io.StringIO(ssh_key.decode("utf-8")))
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
					"key": ssh_key.decode("utf-8") # Send as text
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
