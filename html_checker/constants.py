class ErrorLevel:
    PRIORITY = {
        "success": 0,
        "info": 1,
        "warning": 2,
        "danger": 3,
    }

    def __init__(self, level: str):
        self.level = level

    def __int__(self):
        return self.PRIORITY[self.level]

    def __lt__(self, other):
        return int(self) < int(other)

    def __eq__(self, other):
        return int(self) == int(other)

    def __hash__(self):
        return hash(self.level)

    def __repr__(self):
        return f"ErrorLevel(level='{self.level}')"

SUCCESS = ErrorLevel("success")
WARNING = ErrorLevel("warning")
ERROR = ErrorLevel("danger")
INFO = ErrorLevel("info")


