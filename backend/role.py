from enum import Enum


class Role(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'
    NEW_USER = 'new_user'

    @staticmethod
    def from_str(role_str: str):
        """Converts a string into an equivalent role enum"""
        match role_str:
            case Role.NEW_USER.value:
                return Role.NEW_USER
            case Role.USER.value:
                return Role.USER
            case Role.MANAGER.value:
                return Role.MANAGER
            case Role.ADMIN.value:
                return Role.ADMIN
            case _:
                return None
