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
        selector: str | None = None,
        elem: Tag | None = None,
        many: bool = False,
        prefix: str = "",
        root: Optional["TagChecker"] = None,
        not_exist_error_level: str = ERROR,
    ):
        self._name = name
        self.selector = selector
        self.elem = elem
        self.many = many
        self._root = root
        self.prefix = prefix
        self.errors = {}
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
                nested_tag = deepcopy(attr)
                nested_tag_elem = self.elem.select_one(nested_tag.selector)
                nested_tag.elem = nested_tag_elem
                self._childrens[name] = nested_tag
                setattr(self, name, self._childrens[name])

    @property
    def attributes(self) -> dict[str, HtmlTagAttribute]:
        return self._attributes

    @property
    def childrens(self) -> dict[str, "TagChecker"]:
        return self._childrens

    def get_short_display(self) -> str:
        return f"<{self.elem.name} {self.elem.attrs}>...</{self.elem.name}>"


    def run_validators(self) -> None:
        self.run_attributes_validation()
        self.run_children_validation()

        self.collect_attributes_errors()

    def collect_attributes_errors(self) -> None:
        for attribute_name, attribute in self.attributes.items():
            if self.errors.get(attribute_name) is None:
                self.errors[attribute_name] = []
            self.errors[attribute_name].extend(attribute.errors)

    def run_attributes_validation(self) -> None:
        for attribute_name, attribute in self.attributes.items():
            attribute.run_validators()

    def run_children_validation(self) -> None:
        for children_tag in self.childrens.values():
            children_tag.run_validators()

    def validate(self) -> None:
        """Hook"""

class ListTagChecker(TagChecker):
    pass