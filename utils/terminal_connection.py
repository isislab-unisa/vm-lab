import io
from typing import Dict

import paramiko
import requests
from paramiko.ssh_exception import AuthenticationException


def test_connection(hostname: str, port: int, username: str,
					password: str = None, ssh_key: bytes = None,
					terminal_url: str = "http://localhost:8888") -> Dict[str, str]:
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
			data = {
				"hostname": hostname,
				"port": port,
				"username": username
			}
			files = {
				"ssh_key": ssh_key  # Send as bytes
			}
			response = requests.post(f"{terminal_url}/create-session", data=data, files=files)
		elif password:
			# Test the connection with the password
			ssh_client.connect(
				hostname=hostname,
				port=port,
				username=username,
				password=password
			)
			data = {
				"hostname": hostname,
				"port": port,
				"username": username,
				"password": password
			}
			response = requests.post(f"{terminal_url}/create-session", json=data)
		else:
			raise ValueError("No password or SSH key provided.")

		return response.json()
	except AuthenticationException:
		raise Exception("Authentication failed.")
	except Exception as e:
		raise Exception("Connection failed:", str(e))
	finally:
		# Close the testing connection
		ssh_client.close()
