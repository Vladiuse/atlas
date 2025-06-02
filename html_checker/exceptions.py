from common.exceptions import AppException

from .constants import ERROR, ErrorLevel


class FormNotFound(AppException):
    pass


class ValidationError(Exception):
    def __init__(self, message: str, level: ErrorLevel = ERROR):
        self.message = message
        self.level = level

    def __repr__(self):
        return f"ValidationError(message='{self.message}', level={self.level}"

    def to_detail(self) -> dict:
        return {
            "message": str(self.message),
            "level": str(self.level),
        }
