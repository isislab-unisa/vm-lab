from typing import Type
from sqlalchemy import Column, String, Integer, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship, Session

from .base_model import Base
from backend.fernet_encryption import cipher
from backend.models import User
from utils.other import count_non_none_variables


class VirtualMachine(Base):
	"""Class representing a Virtual Machine in the database."""
	__tablename__ = 'virtual_machines'

	################################
	#        TABLE COLUMNS         #
	################################

	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	host = Column(String(50), nullable=False)
	port = Column(Integer, nullable=False)
	username = Column(String(50), nullable=False)
	password = Column(String(128))
	ssh_key = Column(LargeBinary)

	################################
	#         FOREIGN KEYS         #
	################################

	user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

	################################
	#  RELATIONSHIPS ONE-TO-MANY   #
	################################

	user = relationship("User", back_populates='virtual_machines', lazy='joined')

	################################
	#  SSH KEY ENCRYPTION METHODS  #
	################################

	@staticmethod
	def encrypt_key(key: bytes):
		"""Encrypts an SSH Key."""
		return cipher.encrypt(key)

	def decrypt_key(self):
		"""Decrypts the SSH Key of this Virtual Machine."""
		return cipher.decrypt(self.ssh_key)

	################################
	# PASSWORD ENCRYPTION METHODS  #
	################################

	@staticmethod
	def encrypt_password(password: str):
		"""Encrypts a plain password."""
		return cipher \
			.encrypt(password.encode('utf-8')) \
			.decode('utf-8')

	def decrypt_password(self):
		"""Decrypts the password of this Virtual Machine."""
		return cipher \
			.decrypt(self.password.encode('utf-8')) \
			.decode('utf-8')

	##############################
	#        FIND METHODS        #
	##############################

	@staticmethod
	def find_all(db: Session):
		"""Returns a list with all virtual machines in the database."""
		return db.query(VirtualMachine).all()

	@staticmethod
	def find_by(db: Session,
				vm_id: int = None,
				user_id: int = None,
				user_name: str = None):
		"""
		Shortcut method for simple queries. Only one parameter can be passed.

		For more complex queries, use `db.query` from sqlalchemy.

		:param db: The connection to the database
		:param vm_id: ID of the vm to find, returns a `VirtualMachine` or `None`
		:param user_id: ID of a user to find its virtual machines, returns a list of `VirtualMachine`
		:param user_name: Username of a user to find its virtual machines, returns a list of `VirtualMachine`
		"""
		count = count_non_none_variables([vm_id, user_id, user_name])

		if count != 1:
			raise ValueError(
				f"The find_by function must have exactly one search parameter. "
				f"Passed {count} parameters."
			)

		query = db.query(VirtualMachine)

		if vm_id:
			search_result: VirtualMachine = query \
				.filter(VirtualMachine.id == vm_id) \
				.first()
			return search_result

		elif user_id:
			search_result: list[Type[VirtualMachine]] = query \
				.filter(VirtualMachine.user_id == user_id) \
				.all()
			return search_result

		elif user_name:
			search_result: list[Type[VirtualMachine]] = query \
				.join(VirtualMachine.user) \
				.filter(User.username == user_name) \
				.all()
			return search_result

		else:
			return None

	################################
	#        OTHER METHODS         #
	################################

	def __str__(self):
		return (f"VirtualMachine("
				f"id={self.id}, "
				f"name={self.name}, "
				f"host={self.host}, "
				f"port={self.port}, "
				f"user_id={self.user_id}"
				f")")