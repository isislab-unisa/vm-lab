import bcrypt

from typing import Type
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Session

from .base_model import Base
from backend.role import Role
from utils.other import count_non_none_variables


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
	def find_all(db: Session):
		"""Returns a list with all users in the database."""
		return db.query(User).all()

	@staticmethod
	def find_by(db: Session,
				user_id: int = None,
				user_name: str = None,
				user_email: str = None,
				user_role: Role = None):
		"""
		Shortcut method for simple queries. Only one parameter can be passed.

		For more complex queries, use `db.query` from sqlalchemy.

		:param db: The connection to the database
		:param user_id: ID of the user to find, returns a `User` or `None`
		:param user_name: Username of the user to find, returns a `User` or `None`
		:param user_email: Email of the user to find, returns a `User` or `None`
		:param user_role: Role of the user to find, returns a list of `User`
		"""
		count = count_non_none_variables([user_id, user_name, user_email, user_role])

		if count != 1:
			raise ValueError(
				f"The find_by function must have exactly one search parameter. "
				f"Passed {count} parameters."
			)

		query = db.query(User)

		if user_id:
			search_result: User = query \
				.filter(User.id == user_id) \
				.first()
			return search_result

		elif user_name:
			search_result: User = query \
				.filter(User.username == user_name) \
				.first()
			return search_result

		elif user_email:
			search_result: User = query \
				.filter(User.email == user_email) \
				.first()
			return search_result

		elif user_role:
			role: str = user_role.to_string()
			search_result: list[Type[User]] = query \
				.filter(User.role == role) \
				.all()
			return search_result

		else:
			return None

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
				f"vm_count={len(self.virtual_machines)}, "
				f"bookmark_count={len(self.bookmarks)}"
				f")")