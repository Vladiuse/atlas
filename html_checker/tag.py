from copy import deepcopy
from typing import Optional

from bs4 import Tag

from .constants import ERROR
from .dto import Error
from .tag_attribut import HtmlTagAttribute


class TagChecker:
    def __init__(  # noqa: PLR0913
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
        self._bind_fields()

    def _bind_fields(self) -> None:
        if hasattr(self, "_attributes") or hasattr(self, "_childrens"):
            raise RuntimeError("Fields already bound")
        self._attributes: dict[str, HtmlTagAttribute] = {}
        self._childrens: dict[str, TagChecker] = {}
        for name in dir(self.__class__):
            if name.startswith(("__", "_")) and name != "_class":
                continue
            attr = getattr(self.__class__, name)
            if isinstance(attr, HtmlTagAttribute):
                tag_attribute = deepcopy(attr)
                self._attributes[name] = tag_attribute
                setattr(self, name, tag_attribute)
                tag_attribute.bind(root=self, field_name=name)
            elif isinstance(attr, TagChecker):
                self._childrens[name] = deepcopy(attr)
                setattr(self, name, self._childrens[name])

    @property
    def attributes(self) -> dict[str, HtmlTagAttribute]:
        return self._attributes

    @property
    def childrens(self) -> dict[str, "TagChecker"]:
        return self._childrens

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

    def run_checks(self) -> None:
        self.run_nested_checks()

    def run_validators(self) -> None:
        self.run_attributes_validation()
        self.run_children_validation()

    def run_attributes_validation(self) -> None:
        for attribute in self.attributes.values():
            attribute.run_validators()

    def run_children_validation(self) -> None:
        for children_tag in self.childrens.values():
            children_tag.run_validators()

    def validate(self) -> None:
        """Hook"""

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
