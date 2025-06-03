import contextlib
from collections import OrderedDict
from copy import deepcopy
from typing import Callable, Optional

from bs4 import Tag
from bs4.element import AttributeValueList

from . import levels
from .exceptions import ValidationError
from .tag_attribut import HtmlTagAttribute

NON_FIELD_ERROR = "non_field_errors"


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
        not_exist_error_level: str = levels.ERROR,
        elem_number: int | None = None,
    ):
        self.selector = selector if selector else self.SELECTOR
        self.field_name = None
        self.elem = elem
        self.many = many
        self.root = root
        self.prefix = prefix
        self.errors = OrderedDict()
        self.required = required
        self.not_exist_error_level = not_exist_error_level
        self.elem_number = elem_number
        self._bind_fields()

        if not any([self.elem, self.selector]):
            raise AttributeError("One of the parameter elem or selector must be set")

    def _bind_fields(self) -> None:
        if hasattr(self, "_fields"):
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
        for attribute_field_name, attribute in self.attributes.items():
            with contextlib.suppress(KeyError):
                attribute_value = self.elem[attribute.name]
                if isinstance(attribute_value, AttributeValueList):
                    attribute_value = " ".join(attribute_value)
                attribute.value = attribute_value

    def _fill_childrens(self) -> None:
        for child_name, children in self.childrens.items():
            # elem = self.elem.select_one(children.selector)
            # children.elem = elem
            children.find_elem()
            children.fill()

    def exist(self) -> bool:
        return bool(self.elem)

    def is_list_tag(self) -> bool:
        return False

    @property
    def attributes(self) -> dict[str, HtmlTagAttribute]:
        return {field_name: field for field_name, field in self._fields.items() if isinstance(field, HtmlTagAttribute)}

    @property
    def childrens(self) -> dict[str, "TagChecker"]:
        return {field_name: field for field_name, field in self._fields.items() if isinstance(field, TagChecker)}

    def get_short_display(self) -> str:
        if self.elem:
            return f"<{self.elem.name} {self.elem.attrs}>...</{self.elem.name}>"
        return ""

    @property
    def tag_name(self) -> str:
        return self.elem.name if self.elem else "None"

    @property
    def path_name(self) -> str:
        name = self.selector if self.selector else self.tag_name
        if self.elem_number:
            name = f"{name}-{self.elem_number}"
        if self.root and self.root.tag_name != "html":
            name = f"{self.root.path_name} > {name}"
        return name

    @property
    def error_level(self) -> levels.ErrorLevel:
        # get attributes level errors
        max_attribute_error_level = levels.SUCCESS
        if len(self.attributes) != 0:
            attributes_levels: list[levels.ErrorLevel] = []
            for attribute in self.attributes.values():
                attributes_levels.append(attribute.error_level)
            max_attribute_error_level = max(attributes_levels)
        # get non_fields (self) level errors
        if self.errors.get(NON_FIELD_ERROR):
            max_level_error = max(self.errors[NON_FIELD_ERROR], key=lambda validation_error: validation_error.level)
            self_error_level = max_level_error.level
            return max(self_error_level, max_attribute_error_level)
        return max_attribute_error_level

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
                self.errors.setdefault(NON_FIELD_ERROR, []).append(error)

    def _run_fields_validation(self) -> None:
        for field_name, field in self._fields.items():
            field.run_validators()
            # run validation from methods validate_<field_name>
            self._run_custom_field_validator(field_name=field_name)  # must be called after field.run_validators()
            # collect field errors
            if len(field.errors) != 0:
                self.errors[field_name] = field.errors

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
                    if field.many is False:
                        field.errors.setdefault(NON_FIELD_ERROR, []).append(error)
                    else:
                        self.errors.setdefault(NON_FIELD_ERROR, []).append(error)
                elif isinstance(field, HtmlTagAttribute):
                    field.errors.append(error)
                else:
                    raise TypeError(f"Unknown class type of field {type(field)}")

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
        self.many = True
        self.root = None
        self.field_name = None
        self.items = []
        self.errors = []

    def __iter__(self):
        return iter(self.items)

    def bind(self, root: "TagChecker", field_name: str) -> None:
        self.root = root
        self.field_name = field_name

    def find_elem(self) -> None:
        elements = self.root.elem.select(self.field.selector)
        for elem_number, elem in enumerate(elements):
            field = deepcopy(self.field)
            field.bind(root=self.root, field_name=self.field_name)
            field.elem = elem
            field.elem_number = elem_number + 1
            self.items.append(field)

    def run_validators(self) -> None:
        try:
            self._required_validation()
        except ValidationError as error:
            self.root.errors.setdefault(NON_FIELD_ERROR, []).append(error)
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
            raise ValidationError(f"Must provide at least one item: {self.field.name}")

    def is_list_tag(self) -> bool:
        return True
