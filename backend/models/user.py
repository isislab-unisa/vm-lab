from __future__ import annotations
# https://stackoverflow.com/a/55344418

import bcrypt
from typing import Type, List, cast
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship, Session

from .base_model import Base
from backend.role import Role


class User(Base):
	"""Class representing a User in the database."""
	__tablename__ = 'users'

	################################
	#        TABLE COLUMNS         #
	################################

	id = Column(Integer, primary_key=True)
	username = Column(String(50), unique=True, nullable=False, index=True)
	email = Column(String(100), unique=True, nullable=False)
	password = Column(String(128), nullable=False)  # Hashed password
	role = Column(String(10), nullable=False)
	first_name = Column(String(50), nullable=False)
	last_name = Column(String(50), nullable=False)
	disabled = Column(Boolean, nullable=False, default=False)

	################################
	#  RELATIONSHIPS ONE-TO-MANY   #
	################################

	virtual_machines = relationship("VirtualMachine", back_populates="user", lazy='joined')
	bookmarks = relationship("Bookmark", back_populates="user", lazy='joined')

	################################
	# PASSWORD ENCRYPTION METHODS  #
	################################

	@staticmethod
	def hash_password(plain_password) -> str:
		"""
		Hashes a plain text password.

		:return: The hashed password as a string.
		"""
		return bcrypt \
			.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()) \
			.decode('utf-8')


	def verify_password(self, plain_password) -> bool:
		"""
		Verifies a plain text password against the hashed one.

		:return: True if the password matches, False otherwise.
		"""
		return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))

	##############################
	#        FIND METHODS        #
	##############################

	@staticmethod
	def find_all(db: Session,
				 disabled: bool = None,
				 exclude_user_id: int = None,
				 exclude_user_name: str = None,
				 exclude_user_roles: list[Role] = None
				 ) -> list[User]:
		"""
		Find all users in the database, eventually excluding one of them or/and an entire role.
		:param db: The database session obtained with get_db()
		:param disabled: If the user must be disabled or not
		:param exclude_user_id: The id of the user to exclude
		:param exclude_user_name: The name of the user to exclude
		:param exclude_user_roles: The roles to exclude
		:return A list of users
		"""
		query = db.query(User)

		if disabled is not None:
			query = query.filter(User.disabled == disabled)

		if exclude_user_id is not None:
			query = query.filter(User.id != exclude_user_id)
		elif exclude_user_name is not None:
			query = query.filter(User.username != exclude_user_name)

		if exclude_user_roles is not None:
			for role in exclude_user_roles:
				query = query.filter(User.role != role.value)

		query_result: list[Type[User]] = query.all()
		return cast(List[User], query_result)


	@staticmethod
	def find_by_id(db: Session, user_id: int) -> User | None:
		"""
		Find a user by its id.
		:param db: The database session obtained with get_db()
		:param user_id: The id of the user
		:return A user if it has been found, otherwise `None`
		"""
		return (db.query(User)
				.filter(User.id == user_id)
				.first())


	@staticmethod
	def find_by_user_name(db: Session, user_name: str) -> User | None:
		"""
		Find a user by its username.
		:param db: The database session obtained with get_db()
		:param user_name: Username of the user
		:return: A user if it has been found, otherwise `None`
		"""
		return (db.query(User)
				.filter(User.username == user_name)
				.first())


	@staticmethod
	def find_by_email(db: Session, email: str) -> User | None:
		"""
		Find a user by its email.
		:param db: The database session obtained with get_db()
		:param email: Email of the user
		:return: A user if it has been found, otherwise `None`
		"""
		return (db.query(User)
				.filter(User.email == email)
				.first())


	@staticmethod
	def find_by_role(db: Session, role: Role,
					 exclude_user_id: int = None,
					 exclude_user_name: str = None,
					 ) -> list[User]:
		"""
		Find all users in the database with a specific role, eventually excluding one of them.
		:param db: The database session obtained with get_db()
		:param role: The role to search for
		:param exclude_user_id: The id of the user to exclude
		:param exclude_user_name: The name of the user to exclude
		:return A list of users
		"""
		query = db.query(User)

		if exclude_user_id is not None:
			query = query.filter(User.id != exclude_user_id)
		elif exclude_user_name is not None:
			query = query.filter(User.username != exclude_user_name)

		query_result: list[Type[User]] = (query
				.filter(User.role == role.value)
				.all())
		return cast(List[User], query_result)


	################################
	#        OTHER METHODS         #
	################################

	def to_credentials_dict(self):
		"""Creates a dict readable by the streamlit-authentication authenticator object."""
		return {
			'email': self.email,
			'first_name': self.first_name,
			'last_name': self.last_name,
			'password': self.password,
			'roles': self.role,
		}

	def __str__(self):
		return (f"User("
				f"id={self.id}, "
				f"role={self.role}, "
				f"username={self.username}, "
				f"password={self.password}, "
				f"email={self.email}, "
				f"first_name={self.first_name}, "
				f"last_name={self.last_name}, "
				f"disabled={self.disabled}, "
				f"vm_count={len(self.virtual_machines)}, "
				f"bookmark_count={len(self.bookmarks)}"
				f")")