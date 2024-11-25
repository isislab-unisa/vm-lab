import yaml
import streamlit as st

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from yaml import SafeLoader

from backend.models import User

#################################
#     DATABASE CREDENTIALS      #
#################################

db_username = st.secrets['db_username']
db_password = st.secrets['db_password']
db_address = st.secrets['db_address']
db_name = st.secrets['db_name']
DATABASE_URL = f"postgresql+psycopg2://{db_username}:{db_password}@{db_address}/{db_name}"

################################
#       DATABASE SESSION       #
################################

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Session:
	"""Context manager to provide a database session."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


##################################
#       Load Initial Users       #
##################################

# TODO: Initialize database if it does not exist
def load_initial_users():
	"""
    Loads initial users into the database from a YAML file if the users table is empty.
    """
	with get_db() as db:
		if db.query(User).count() == 0:
			with open('first_users.yaml') as file:
				initial_users = yaml.load(file, Loader=SafeLoader)
				for user_data in initial_users['first_users']:
					new_user = User(
						username=user_data['username'],
						password=User.hash_password(user_data['password']),
						email=user_data['email'],
						first_name=user_data['first_name'],
						last_name=user_data['last_name'],
						role=user_data['role']
					)
					db.add(new_user)
					db.commit()
					print("Added initial user:", new_user)


load_initial_users()
