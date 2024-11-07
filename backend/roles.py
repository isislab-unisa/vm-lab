from enum import Enum


class Roles(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'
    NEW_USER = 'new_user'

    @staticmethod
    def from_str(role_str: str):
        """Converts a string into an equivalent role enum"""
        match role_str:
            case Roles.NEW_USER.value:
                return Roles.NEW_USER
            case Roles.USER.value:
                return Roles.USER
            case Roles.MANAGER.value:
                return Roles.MANAGER
            case Roles.ADMIN.value:
                return Roles.ADMIN
            case _:
                return None
