import contextlib
from copy import deepcopy
from typing import Callable, Optional

from bs4 import Tag

from .constants import ERROR
from .exceptions import ValidationError
from .tag_attribut import HtmlTagAttribute


class TagChecker:
    SELECTOR = None
    def __init__(  # noqa: PLR0913
        self,
        selector: str | None = None,
        elem: Tag | None = None,
        many: bool = False,
        required: bool = True,
        prefix: str = "",
        root: Optional["TagChecker"] = None,
        not_exist_error_level: str = ERROR,
    ):
        self.selector = selector if selector else self.SELECTOR
        self.field_name = None
        self.elem = elem
        self.many = many
        self.root = root
        self.prefix = prefix
        self.errors = {}
        self.required = required
        self.not_exist_error_level = not_exist_error_level
        self._bind_fields()

        if not any([self.elem, self.selector]):
            raise AttributeError('One of the parameter elem or selector must be set')

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
                self._fields[name] = field
                setattr(self, name, field)
                field.bind(root=self, field_name=name)
            elif isinstance(attr, TagChecker):
                field = ListTagChecker(field=attr) if attr.many else deepcopy(attr)
                self._fields[name] = field
                setattr(self, name, field)
                field.bind(root=self, field_name=name)

    def bind(self, root: "TagChecker", field_name: str) -> None:
        self.root = root
        self.field_name = field_name

    def fill(self) -> None:
        if self.elem is not None:
            self._fill_attributes()
            self._fill_childrens()

    def find_elem(self) -> None:
        self.elem = self.root.elem.select_one(self.selector)

    def _fill_attributes(self) -> None:
        for attribute_name, attribute in self.attributes.items():
            with contextlib.suppress(KeyError):
                attribute.value = self.elem[attribute_name]

    def _fill_childrens(self) -> None:
        for child_name, children in self.childrens.items():
            # elem = self.elem.select_one(children.selector)
            # children.elem = elem
            children.find_elem()
            children.fill()

    @property
    def attributes(self) -> dict[str, HtmlTagAttribute]:
        return {field_name: field for field_name, field in self._fields.items() if isinstance(field, HtmlTagAttribute)}

    @property
    def childrens(self) -> dict[str, "TagChecker"]:
        return {field_name: field for field_name, field in self._fields.items() if isinstance(field, TagChecker)}

    def get_short_display(self) -> str:
        if self.elem:
            return f"<{self.elem.name} {self.elem.attrs}>...</{self.elem.name}>"
        return "None"

    def run_validators(self) -> None:
        self.fill()  # заполняет классы объектами bs4 Tag
        self._run_non_fields_validators()
        if self.elem is not None:  # запускать валидацию атрибутов и вложенных тегов только если текущий тэг найден
            self._run_fields_validation()

    def _run_non_fields_validators(self) -> None:
        non_fields_validators = [self._required_validation, self.validate]
        for validator in non_fields_validators:
            try:
                validator()
            except ValidationError as error:
                if self.errors.get("non_field_errors") is None:
                    self.errors["non_field_errors"] = []
                self.errors["non_field_errors"].append(error)

    def _run_fields_validation(self) -> None:
        for field_name, field in self._fields.items():
            field.run_validators()
            if len(field.errors) != 0:
                self.errors[field_name] = field.errors
            self._run_custom_field_validator(field_name=field_name)  # must be called after field.run_validators()

    def _get_custom_field_validator(self, field_name: str) -> Callable | None:
        method_field_validation_name = f"validate_{field_name}"
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method) and method_name == method_field_validation_name:
                return method
        return None

    def _run_custom_field_validator(self, field_name: str) -> None:
        method = self._get_custom_field_validator(field_name=field_name)
        if method is not None:
            field = getattr(self, field_name)
            try:
                method(field=field)
            except ValidationError as error:
                field = getattr(self, field_name)
                if isinstance(field, TagChecker):
                    self.errors.setdefault(field_name, {}).setdefault("non_field_errors", []).append(error)
                elif isinstance(field, HtmlTagAttribute):
                    self.errors.setdefault(field_name, []).append(error)

    def _required_validation(self) -> None:
        if self.required and self.elem is None:
            raise ValidationError(
                message=f"Tag {self.__class__.__name__} required",
            )

    def validate(self) -> None:
        """Hook"""


class ListTagChecker(TagChecker):
    def __init__(self, field: TagChecker):
        self.field = field
        self.root = None
        self.field_name = None
        self.items = []
        self.errors = []

    def bind(self, root: "TagChecker", field_name: str) -> None:
        self.root = root
        self.field_name = field_name

    def find_elem(self) -> None:
        elements =  self.root.elem.select(self.field.selector)
        for elem in elements:
            field = deepcopy(self.field)
            field.bind(root=self.root, field_name=self.field_name)
            field.elem = elem
            self.items.append(field)

    def run_validators(self) -> None:
        try:
            self._required_validation()
        except ValidationError as error:
            self.errors.append(error)
            return
        for field in self.items:
            field.run_validators()
        for field in self.items:
            self.errors.append(field.errors)

    def fill(self) -> None:
        for field in self.items:
            field.fill()

    def _required_validation(self) -> None:
        if self.field.required and len(self.items) == 0:
            raise ValidationError('Must provide at least one item')

