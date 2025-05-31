from copy import deepcopy
from typing import Optional

from bs4 import Tag

from .constants import ERROR
from .dto import Error
from .exceptions import ValidationError

class HtmlTagAttribute:

    def __init__(self,
                 name: str = "",
                 root: Optional["TagChecker"] = None,
                 required: bool = False,
                 ):
        self.name = name
        self.root = root
        self.required = required


class TagChecker:
    def __init__( # noqa: PLR0913
        self,
        name: str = "",
        elem: Tag | None = None,
        selector: str | None = None,
        prefix: str = "",
        root: Optional["TagChecker"] = None,
        not_exist_error_level: str = ERROR,
    ):
        self._name = name
        self.selector = selector
        self._root = root
        self.prefix = prefix
        self._elem = elem
        self.errors = []
        self.not_exist_error_level = not_exist_error_level

    def bind_fields(self) -> None:
        if hasattr(self, 'attributes_fields') or hasattr(self, 'nested_fields'):
            raise RuntimeError("Fields already bound")
        self.attributes_fields = {}
        self.nested_fields = {}
        for name in dir(self.__class__):
            if name.startswith(("__", "_")):
                continue
            attr = getattr(self.__class__, name)
            if isinstance(attr, HtmlTagAttribute):
                self.attributes_fields[name] = deepcopy(attr)
                setattr(self, name, self.attributes_fields[name])
            elif isinstance(attr, TagChecker):
                self.nested_fields[name] = deepcopy(attr)
                setattr(self, name, self.nested_fields[name])

    def get_short_display(self) -> str:
        return f"<{self.elem.name} {self.elem.attrs}>...</{self.elem.name}>"

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value

    def _get_nested_tags(self) -> list["TagChecker"]:
        tags = []
        for name in dir(self):
            checker = getattr(self, name)
            if name not in ["root", "_root"] and isinstance(checker, TagChecker):
                new_checker = deepcopy(checker)
                new_checker.root = self
                elem = self.elem.select_one(new_checker.selector)
                new_checker.elem = elem
                new_checker.name = name
                tags.append(new_checker)
        return tags

    @property
    def elem(self) -> Tag:
        return self._elem

    @elem.setter
    def elem(self, value: Tag) -> None:
        self._elem = value

    @property
    def name(self) -> str:
        name = self._name
        if self.prefix:
            name = f"{self.prefix}_{self._name}"
        if self.root:
            return f"{self.root.name}.{name}"
        return name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def attr_value_eq(self, attr_name: str, value: str, *, ignore_case: bool = False) -> bool:
        try:
            attr_value = self.elem[attr_name]
            if ignore_case is True:
                return attr_value.lower() == value.lower()
            return attr_value == value
        except KeyError:
            return False

    def get_attr_value(self, attr_name: str) -> str | None:
        try:
            return self.elem[attr_name]
        except KeyError:
            return None

    def _get_checks_methods(self) -> list:
        methods = []
        for name in dir(self):
            if name.startswith("check_"):
                method = getattr(self, name)
                if callable(method):
                    methods.append(method)
        return methods

    def run_checks(self) -> None:
        self.run_methods_checks()
        self.run_nested_checks()

    def run_nested_checks(self) -> None:
        nested_tags = self._get_nested_tags()
        for nested_checker in nested_tags:
            if nested_checker.elem is None:
                error = Error(
                    check_name=f"{self.name}.{nested_checker.__class__.__name__}:elem_exists",
                    message=f"{nested_checker.selector} not found",
                    level=nested_checker.not_exist_error_level,
                    elem="",
                )
                self.errors.append(error)
            else:
                nested_checker.run_checks()
                self.errors.extend(nested_checker.errors)

    def run_methods_checks(self) -> None:
        checkers = self._get_checks_methods()
        for checker in checkers:
            try:
                checker()
            except ValidationError as e:
                error = Error(
                    check_name=f"{self.name}:{checker.__name__}",
                    message=e.message,
                    level=e.level,
                    elem=self.get_short_display(),
                )
                self.errors.append(error)
