import contextlib
from copy import deepcopy
from typing import Optional

from bs4 import Tag

from .constants import ERROR
from .exceptions import ValidationError
from .tag_attribut import HtmlTagAttribute


class TagChecker:
    def __init__(  # noqa: PLR0913
        self,
        name: str = "",
        selector: str | None = None,
        elem: Tag | None = None,
        many: bool = False,
        required: bool = True,
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
        self.required = required
        self.not_exist_error_level = not_exist_error_level
        self._bind_fields()

    def _bind_fields(self) -> None:
        if hasattr(self, "_attributes") or hasattr(self, "_childrens"):
            raise RuntimeError("Fields already bound")
        self._fields: dict[str, HtmlTagAttribute | TagChecker] = {}
        for name in dir(self.__class__):
            if name.startswith(("__", "_")) and name != "_class":
                continue
            attr = getattr(self.__class__, name)
            if isinstance(attr, HtmlTagAttribute):
                field = deepcopy(attr)
                field.bind(root=self, field_name=name)
                self._fields[name] = field
                setattr(self, name, field)
            elif isinstance(attr, TagChecker):
                field = deepcopy(attr)
                self._fields[name] = field
                setattr(self, name, field)

    def fill(self) -> None:
        if self.elem is not None:
            self._fill_attributes()
            self._fill_childrens()

    def _fill_attributes(self) -> None:
        for attribute_name, attribute in self.attributes.items():
            with contextlib.suppress(KeyError):
                attribute.value = self.elem[attribute_name]

    def _fill_childrens(self) -> None:
        for child_name, children in self.childrens.items():
            elem = self.elem.select_one(children.selector)
            children.elem = elem
            children.fill()

    @property
    def attributes(self) -> dict[str, HtmlTagAttribute]:
        return {field_name: field for field_name, field in self._fields.items() if isinstance(field, HtmlTagAttribute)}

    @property
    def childrens(self) -> dict[str, "TagChecker"]:
        return {field_name: field for field_name, field in self._fields.items() if isinstance(field, TagChecker)}

    def get_short_display(self) -> str:
        return f"<{self.elem.name} {self.elem.attrs}>...</{self.elem.name}>"

    def run_validators(self) -> None:
        self.fill()  # заполняет классы объектами bs4 Tag
        self.run_non_fields_validators()
        if self.elem is not None:  # запускать валидацию атрибутов и вложенных тегов только если текущий тэг найден
            self.run_fields_validation()
            self.collect_fields_errors()

    def run_non_fields_validators(self) -> None:
        non_fields_validators = [self.required_validation, self.validate]
        for validator in non_fields_validators:
            try:
                validator()
            except ValidationError as error:
                if self.errors.get("non_field_errors") is None:
                    self.errors["non_field_errors"] = []
                self.errors["non_field_errors"].append(error)

    def collect_fields_errors(self) -> None:
        for field_name, field in self._fields.items():
            if len(field.errors) != 0:
                self.errors[field_name] = field.errors

    def run_fields_validation(self) -> None:
        for field in self._fields.values():
            field.run_validators()

    def required_validation(self) -> None:
        if self.required and self.elem is None:
            raise ValidationError(
                message=f"Tag {self.__class__.__name__} required",
            )

    def validate(self) -> None:
        """Hook"""


class ListTagChecker(TagChecker):
    pass
