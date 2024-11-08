# vm-lab
[![Python Version](https://img.shields.io/badge/Python-3.12.7-blue?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3127/)

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
db_username = "username"
db_password = "password"
db_address = "localhost or ip"
db_name = "name"

cookie_name = "cooke_name"
cookie_key = "key"
cookie_expiry_days = 30
```

These are used in `backend/database.py` to create the connection.


## Database
```postgresql
CREATE DATABASE "vm-lab"
    WITH
    OWNER = postgres
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
    ip VARCHAR(50) NOT NULL,
    bookmark BOOL NOT NULL,
    user_id SERIAL NOT NULL, 
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE 
);
```
