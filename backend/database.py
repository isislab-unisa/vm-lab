from contextlib import contextmanager
import yaml
from yaml.loader import SafeLoader
import bcrypt
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

db_username = st.secrets['db_username']
db_password = st.secrets['db_password']
db_address = st.secrets['db_address']
db_name = st.secrets['db_name']
DATABASE_URL = f"postgresql+psycopg2://{db_username}:{db_password}@{db_address}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	username = Column(String(50), unique=True, nullable=False, index=True)
	email = Column(String(100), unique=True, nullable=False)
	password = Column(String(128), nullable=False)  # Hashed password
	role = Column(String(10), nullable=False)
	first_name = Column(String(50), nullable=False)
	last_name = Column(String(50), nullable=False)

	# one-to-many relationship
	virtual_machines = relationship("VirtualMachine", back_populates="user", lazy='joined')

	@staticmethod
	def hash_password(plain_password):
		return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

	def verify_password(self, plain_password):
		return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))

	def __str__(self):
		return (f"User(id={self.id}, role={self.role}, username={self.username}, password={self.password}, "
				f"email={self.email}, first_name={self.first_name}, last_name={self.last_name}, "
				f"vm_count={len(self.virtual_machines)})")


class VirtualMachine(Base):
	__tablename__ = 'virtual_machines'
	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	ip = Column(String(50), nullable=False)
	bookmark = Column(Boolean, nullable=False)
	user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

	# Parent of the one-to-many relationship
	user = relationship("User", back_populates='virtual_machines', lazy='joined')

	def __str__(self):
		return (f"VirtualMachine(id={self.id}, name={self.name}, ip={self.ip}, bookmark={self.bookmark}, "
				f"user_id={self.user_id})")


@contextmanager
def get_db() -> Session:
	db = SessionLocal()

	try:
		yield db
	finally:
		db.close()


def get_credentials():
	credentials = {"usernames": {}}
	with get_db() as db:
		users = db.query(User).all()

		if len(users) == 0:
			with open('first_users.yaml') as file:
				users = yaml.load(file, Loader=SafeLoader)["usernames"]

		for user in users:
			credentials["usernames"][user.username] = {
				"email": user.email,
				"first_name": user.first_name,
				"last_name": user.last_name,
				"password": user.password,
				"roles": [user.role],
				"test_vms": user.virtual_machines
			}

		return credentials


db_empty_users = SessionLocal()

if db_empty_users.query(User).count() == 0:
	with open('first_users.yaml') as initial_users_file:
		initial_users = yaml.load(initial_users_file, Loader=SafeLoader)
		for initial_user in initial_users:
			new_user = User(
				username=initial_user['username'],
				password=User.hash_password(initial_user['password']),
				email=initial_user['email'],
				first_name=initial_user['first_name'],
				last_name=initial_user['last_name'],
				role=initial_user['role']
			)
			db_empty_users.add(new_user)
			db_empty_users.commit()
			print("Added initial user:", new_user)
