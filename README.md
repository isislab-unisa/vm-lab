# vm-lab
[![Python Version](https://img.shields.io/badge/Python-3.12.8-blue?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3128/)

Manage all your VMs in the browser.

## Update pip requirements
```shell
pip install -r requirements.txt
```

## Run
After having installed all the requirements, run this in venv:
```shell
streamlit run app.py
```


## Useful stuff (for PyCharm)
### Update the pip requirements

Search everywhere:
`Sync Python Requirements...`

1. `Tools`
2. `Sync Python Requirements...`


## Secrets
Create a `.streamlit/secrets.toml` file and write this:
```toml
################################
#     DATABASE CONNECTION      #
################################
db_username = "username"
db_password = "password"
db_address = "localhost" # or "127.0.0.1" or ip
db_name = "vm-lab"

################################
#     AUTHORIZATION COOKIE     #
################################
cookie_name = "cookie name"
cookie_key = "key"
cookie_expiry_days = 30

################################
#    SENSITIVE DATA CIPHER     #
################################
cipher_key = "some Fernet compliant key"

################################
#       SUPPORT MODULES        #
################################

# URL of the modules
ssh_module_url = "http://localhost:8888"   # or http://ip:port
sftp_module_url = "http://localhost:8261"  # or http://ip:port

# Format to describe how to put the ID for the connection
# Use these variables:
# $URL -> The ssh and sftp module url written above
# $CONNECTION_ID -> The ID obtained from the modules to connect
ssh_url_id_format = "$URL/$CONNECTION_ID"
sftp_url_id_format = "$URL/?connection=$CONNECTION_ID"
```

You can generate the Fernet key in the python console:
```python
>> from cryptography.fernet import Fernet 
>> Fernet.generate_key()
```

## Database
```postgresql
CREATE DATABASE "vm-lab"
    WITH
    OWNER = postgres -- or another user
    ENCODING = 'UTF8'
    LOCALE_PROVIDER = 'libc'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
```

```postgresql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(10) NOT NULL
);
```

```postgresql
CREATE TABLE virtual_machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    host VARCHAR(50) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL,
    ssh_key BYTEA,
    password VARCHAR(128),
    user_id INTEGER NOT NULL, 
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE 
);
```

```postgresql
CREATE TABLE bookmarks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    link VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL, 
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE 
);
```
