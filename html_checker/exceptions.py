from dataclasses import dataclass

from common.exceptions import AppException

from .constants import ERROR


class FormNotFound(AppException):
    pass


@dataclass
class ValidationError(Exception):
    message: str
    level: str = ERROR
