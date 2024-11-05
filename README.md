# vm-lab
Manage all your VMs in the browser.

Using [Python 3.12.7](https://www.python.org/downloads/release/python-3127/).

---
## Useful stuff (for PyCharm)
### Update the pip requirements

Search everywhere:
`Sync Python Requirements...`

1. `Tools`
2. `Sync Python Requirements...`

---
## Secrets
Create a `.streamlit/secrets.toml` file and write this:
```toml
db_username = "username"
db_password = "password"
db_address = "localhost or ip"
db_name = "name"
```

These are used in `backend/database.py` to create the connection.
