from __future__ import annotations
# https://stackoverflow.com/a/55344418

from typing import Type, cast, List
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session

from .base_model import Base
from backend.models import User


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
	def find_all(db: Session,
				 exclude_user_id: int = None,
				 exclude_user_name: str = None,
				 ) -> list[Bookmark]:
		"""
		Find all bookmarks in the database, eventually excluding those belonging to a specific user.
		:param db: The database session obtained with get_db()
		:param exclude_user_id: The id of the user to exclude
		:param exclude_user_name: The name of the user to exclude
		:return A list of bookmarks
		"""
		query = db.query(Bookmark)

		if exclude_user_id is not None:
			query = query.filter(Bookmark.user_id != exclude_user_id)
		elif exclude_user_name is not None:
			query = query.join(User).filter(User.username != exclude_user_name)

		query_result: list[Type[Bookmark]] = query.all()
		return cast(List[Bookmark], query_result)


	@staticmethod
	def find_by_id(db: Session, bookmark_id: int) -> Bookmark | None:
		"""
		Find a bookmark by its id.
		:param db: The database session obtained with get_db()
		:param bookmark_id: The id of the bookmark
		:return A bookmark if it has been found, otherwise `None`
		"""
		return (db.query(Bookmark)
				.filter(Bookmark.id == bookmark_id)
				.first())


	@staticmethod
	def find_by_user_id(db: Session, user_id: int) -> list[Bookmark]:
		"""
		Find all bookmarks in the database owned by a user with a specific id.
		:param db: The database session obtained with get_db()
		:param user_id: The id of the user
		:return: A list of bookmarks owned by a user
		"""
		query_result: list[Type[Bookmark]] = (db.query(Bookmark)
				.filter(Bookmark.user_id == user_id)
				.all())

		return cast(List[Bookmark], query_result)


	@staticmethod
	def find_by_user_name(db: Session, user_name: str) -> list[Bookmark]:
		"""
		Find all bookmarks in the database owned by a user with a specific name.
		:param db: The database session obtained with get_db()
		:param user_name: The username of the user
		:return: A list of bookmarks owned by a user
		"""
		query_result: list[Type[Bookmark]] = (db.query(Bookmark)
				.join(Bookmark.user)
				.filter(User.username == user_name)
				.all())

		return cast(List[Bookmark], query_result)


	################################
	#        OTHER METHODS         #
	################################

	def __str__(self):
		return (f"Bookmark("
				f"id={self.id}, "
				f"name={self.name}, "
				f"user_id={self.user_id}, "
				f"link={self.link}"
				f")")