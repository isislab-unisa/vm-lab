from __future__ import annotations
# https://stackoverflow.com/a/55344418

from typing import Type, cast, List
from sqlalchemy import Column, String, Integer, LargeBinary, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Session

from .base_model import Base
from backend.fernet_encryption import cipher
from backend.models import User


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
	shared = Column(Boolean, nullable=False, default=True)

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
	def find_all(db: Session,
				 shared: bool = None,
				 exclude_user_id: int = None,
				 exclude_user_name: str = None
				 ) -> list[VirtualMachine]:
		"""
		Find all virtual machines in the database. Two optional types of filters can be activated at the same time:
		- Exclusion of vms that belong to a specific user (using the id or the username)
		- Filtering based on the 'shared' flag.
		:param db: The database session obtained with get_db()
		:param shared: Shows only virtual machines marked as shared or not if this parameter is set
		:param exclude_user_id: The id of the user to exclude
		:param exclude_user_name: The name of the user to exclude
		:return A list of virtual machines
		"""
		query = db.query(VirtualMachine)

		if shared is not None:
			query = query.filter(VirtualMachine.shared == shared)

		if exclude_user_id is not None:
			query = query.filter(VirtualMachine.user_id != exclude_user_id)
		elif exclude_user_name is not None:
			query = query.join(User).filter(User.username != exclude_user_name)

		query_result: list[Type[VirtualMachine]] = query.all()

		return cast(List[VirtualMachine], query_result)


	@staticmethod
	def find_by_id(db: Session, vm_id: int) -> VirtualMachine | None:
		"""
		Find a virtual machine by its id.
		:param db: The database session obtained with get_db()
		:param vm_id: The id of the virtual machine
		:return A virtual machine if it has been found, otherwise `None`
		"""
		return (db.query(VirtualMachine)
				.filter(VirtualMachine.id == vm_id)
				.first())


	@staticmethod
	def find_by_user_id(db: Session, user_id: int, shared: bool = None) -> list[VirtualMachine]:
		"""
		Find all virtual machines in the database owned by a user with a specific id.
		Can optionally filter in or out vms that are shared.
		:param db: The database session obtained with get_db()
		:param user_id: The id of the user
		:param shared: Whether the vm is shared
		:return: A list of virtual machines owned by a user
		"""
		query = db.query(VirtualMachine)

		if shared is not None:
			query = query.filter(VirtualMachine.shared == shared)

		query_result: list[Type[VirtualMachine]] = (query
				.filter(VirtualMachine.user_id == user_id)
				.all())

		return cast(List[VirtualMachine], query_result)


	@staticmethod
	def find_by_user_name(db: Session, user_name: str, shared: bool = None) -> list[VirtualMachine]:
		"""
		Find all virtual machines in the database owned by a user with a specific name.
		Can optionally filter in or out vms that are shared.
		:param db: The database session obtained with get_db()
		:param user_name: The username of the user
		:param shared: Whether the vm is shared
		:return: A list of virtual machines owned by a user
		"""
		query = db.query(VirtualMachine)

		if shared is not None:
			query = query.filter(VirtualMachine.shared == shared)

		query_result: list[Type[VirtualMachine]] = (query
				.join(VirtualMachine.user)
				.filter(User.username == user_name)
				.all())

		return cast(List[VirtualMachine], query_result)


	################################
	#        OTHER METHODS         #
	################################

	def __str__(self):
		return (f"VirtualMachine("
				f"id={self.id}, "
				f"name={self.name}, "
				f"host={self.host}, "
				f"port={self.port}, "
				f"shared={self.shared}, "
				f"user_id={self.user_id}"
				f")")