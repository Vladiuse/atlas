from dataclasses import dataclass


@dataclass
class Error:
    check_name: str
    message: str
    level: str
    elem: str | None
