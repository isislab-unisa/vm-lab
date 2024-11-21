from typing import cast, List

import yaml
import bcrypt
import streamlit as st
from contextlib import contextmanager

from cryptography.fernet import Fernet
from yaml.loader import SafeLoader
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base

################################
#     Database Connection      #
################################


db_username = st.secrets['db_username']
db_password = st.secrets['db_password']
db_address = st.secrets['db_address']
db_name = st.secrets['db_name']
DATABASE_URL = f"postgresql+psycopg2://{db_username}:{db_password}@{db_address}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

cipher_key = st.secrets["cipher_key"]
cipher = Fernet(cipher_key)


@contextmanager
def get_db() -> Session:
	"""Context manager to provide a database session."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


################################
#       Database Models        #
################################


Base = declarative_base()


class User(Base):
	"""Class representing a User in the database."""
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	username = Column(String(50), unique=True, nullable=False, index=True)
	email = Column(String(100), unique=True, nullable=False)
	password = Column(String(128), nullable=False)  # Hashed password
	role = Column(String(10), nullable=False)
	first_name = Column(String(50), nullable=False)
	last_name = Column(String(50), nullable=False)

	# Relationships one-to-many
	virtual_machines = relationship("VirtualMachine", back_populates="user", lazy='joined')
	bookmarks = relationship("Bookmark", back_populates="user", lazy='joined')

	@staticmethod
	def hash_password(plain_password) -> str:
		"""
		Hashes a plain text password.
		:return: The hashed password as a string.
		"""
		return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

	def verify_password(self, plain_password) -> bool:
		"""
		Verifies a plain text password against the hashed one.
		:return: True if the password matches, False otherwise.
		"""
		return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))

	def to_credentials_dict(self):
		"""Creates a dict readable by the streamlit-authentication authenticator object"""
		return {
			'email': self.email,
			'first_name': self.first_name,
			'last_name': self.last_name,
			'password': self.password,
			'roles': self.role,
		}

	def __str__(self):
		return (f"User(id={self.id}, role={self.role}, username={self.username}, password={self.password}, "
				f"email={self.email}, first_name={self.first_name}, last_name={self.last_name}, "
				f"vm_count={len(self.virtual_machines)}, bookmark_count={len(self.bookmarks)})")


class VirtualMachine(Base):
	"""Class representing a Virtual Machine in the database."""
	__tablename__ = 'virtual_machines'
	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	host = Column(String(50), nullable=False)
	port = Column(Integer, nullable=False)
	username = Column(String(50), nullable=False)
	password = Column(String(128))
	ssh_key = Column(LargeBinary)
	user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

	# Parent of the one-to-many relationship
	user = relationship("User", back_populates='virtual_machines', lazy='joined')

	@staticmethod
	def encrypt_key(key: bytes):
		return cipher.encrypt(key)

	def decrypt_key(self):
		return cipher.decrypt(self.ssh_key)

	@staticmethod
	def encrypt_password(password: str):
		return cipher\
			.encrypt(password.encode('utf-8'))\
			.decode('utf-8')

	def decrypt_password(self):
		return cipher\
			.decrypt(self.password.encode('utf-8'))\
			.decode('utf-8')

	def __str__(self):
		return (f"VirtualMachine(id={self.id}, name={self.name}, host={self.host}, port={self.port}, "
				f"user_id={self.user_id})")


class Bookmark(Base):
	"""Class representing a Virtual Machine in the database."""
	__tablename__ = 'bookmarks'
	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	link = Column(String(255), nullable=False)
	user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

	# Parent of the one-to-many relationship
	user = relationship("User", back_populates='bookmarks', lazy='joined')

	def __str__(self):
		return (f"Bookmark(id={self.id}, name={self.name}, "
				f"user_id={self.user_id}, link={self.ip})")


def get_db_users_credentials() -> dict:
	"""
    Fetches user credentials from the database and organizes them into a dictionary for use in streamlit-authentication.
    :return: A dictionary containing the usernames, emails, first names, last names, passwords, and roles for all
    users in the database.
    """
	credentials = {"usernames": {}}
	with get_db() as db:
		users: List[User] = cast(List[User], db.query(User).all())
		for user in users:
			credentials["usernames"][user.username] = user.to_credentials_dict()
	return credentials


def get_user_virtual_machines(username: str) -> List[VirtualMachine]:
	with get_db() as db:
		fetched_vms = db.query(VirtualMachine) \
			.join(VirtualMachine.user) \
			.filter(User.username == username) \
			.all()

		return cast(List[VirtualMachine], fetched_vms)


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
