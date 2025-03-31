-- !!! WARNING: THIS FILE DOES NOT CREATE THE DATABASE !!!
-- This file is used by the docker compose file, where the db is already created
-- If you need it, you can create it like this
--
-- CREATE DATABASE "vm-lab"
--     WITH
--     OWNER = username
--     ENCODING = 'UTF8'
--     LOCALE_PROVIDER = 'libc'
--     CONNECTION LIMIT = -1
--     IS_TEMPLATE = False;


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(10) NOT NULL,
    disabled BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE virtual_machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    host VARCHAR(50) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL,
    ssh_key BYTEA,
    password VARCHAR(128),
    shared BOOLEAN NOT NULL DEFAULT true,
    assigned_to VARCHAR(50),
    user_id INTEGER NOT NULL, 
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE 
);

CREATE TABLE bookmarks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    link VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL, 
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE 
);