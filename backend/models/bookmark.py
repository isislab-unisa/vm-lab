from typing import Type
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session

from .base_model import Base
from backend.models import User
from utils.other import count_non_none_variables


class Bookmark(Base):
	"""Class representing a Virtual Machine in the database."""
	__tablename__ = 'bookmarks'

	################################
	#        TABLE COLUMNS         #
	################################

	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	link = Column(String(255), nullable=False)

	################################
	#         FOREIGN KEYS         #
	################################

	user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

	################################
	#  RELATIONSHIPS ONE-TO-MANY   #
	################################

	user = relationship("User", back_populates='bookmarks', lazy='joined')

	##############################
	#        FIND METHODS        #
	##############################

	@staticmethod
	def find_all(db: Session):
		"""Returns a list with all bookmarks in the database."""
		return db.query(Bookmark).all()

	@staticmethod
	def find_by(db: Session,
				bookmark_id: int = None,
				user_id: int = None,
				user_name: str = None):
		"""
		Shortcut method for simple queries. Only one parameter can be passed.

		For more complex queries, use `db.query` from sqlalchemy.

		:param db: The connection to the database
		:param bookmark_id: ID of the bookmark to find, returns a `Bookmark` or `None`
		:param user_id: ID of a user to find its virtual machines, returns a list of `VirtualMachine`
		:param user_name: Username of a user to find its virtual machines, returns a list of `VirtualMachine`
		"""
		count = count_non_none_variables([bookmark_id, user_id, user_name])

		if count != 1:
			raise ValueError(
				f"The find_by function must have exactly one search parameter. "
				f"Passed {count} parameters."
			)

		query = db.query(Bookmark)

		if bookmark_id:
			search_result: Bookmark = query \
				.filter(Bookmark.id == bookmark_id) \
				.first()
			return search_result

		elif user_id:
			search_result: list[Type[Bookmark]] = query \
				.join(Bookmark.user) \
				.filter(User.id == user_id) \
				.all()
			return search_result

		elif user_name:
			search_result: list[Type[Bookmark]] = query \
				.join(Bookmark.user) \
				.filter(User.username == user_name) \
				.all()
			return search_result

		else:
			return None

	################################
	#        OTHER METHODS         #
	################################

	def __str__(self):
		return (f"Bookmark("
				f"id={self.id}, "
				f"name={self.name}, "
				f"user_id={self.user_id}, "
				f"link={self.ip}"
				f")")