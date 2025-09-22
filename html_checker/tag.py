import contextlib
from collections import OrderedDict
from copy import deepcopy
from typing import Callable, Optional, Union

from bs4 import Tag
from bs4.element import AttributeValueList

from . import levels
from .exceptions import ValidationError
from .tag_attribut import HtmlTagAttribute

NON_FIELD_ERROR = "non_field_errors"
GET_ELEMENT_METHOD_NAME = 'get_element'


class TagChecker:
    SELECTOR = None
    DEFAULT_ERROR_LEVEL = levels.ERROR

    def __init__(  # noqa: PLR0913
        self,
        selector: str | None = None,
        elem: Tag | None = None,
        many: bool = False,
        required: bool = True,
        root: Optional["TagChecker"] = None,
        not_exist_error_level: str = levels.ERROR,
        elem_number: int | None = None,
        attributes: dict[str,dict] | None = None,
    ):
        self.selector = selector if selector else self.SELECTOR
        self.field_name = None
        self.elem = elem
        self.many = many
        self.root = root
        self.errors = OrderedDict()
        self.required = required
        self.not_exist_error_level = not_exist_error_level
        self.elem_number = elem_number
        self._attributes = attributes
        self._fields: dict[str, HtmlTagAttribute | TagChecker] = {}

    def __repr__(self):
        return f"<Tag:{self.tag_name}>"

    def __str__(self):
        return repr(self)

    def _bind_fields(self) -> None:
        if hasattr(self, "_is_fields_bind"):
            raise RuntimeError("Fields already bound")
        self._fields: dict[str, HtmlTagAttribute | TagChecker] = {}
        for name in dir(self.__class__):
            if name.startswith(("__", "_")) and name != "_class":
                continue
            attr = getattr(self.__class__, name)
            if isinstance(attr, HtmlTagAttribute):
                field = deepcopy(attr)
                self._set_field(field=field, field_name=name)
            elif isinstance(attr, TagChecker):
                field = ListTagChecker(field=attr) if attr.many else deepcopy(attr)
                self._set_field(field=field, field_name=name)
        # for attributes from Tag param
        if self._attributes:
            for name, attribute_data in self._attributes.items():
                field = HtmlTagAttribute(**attribute_data)
                if hasattr(self, name):
                    raise AttributeError(f'{self} already have attribute "{name}" as field.')
                self._set_field(field=field, field_name=name)
        setattr(self, "_is_fields_bind", True)

    def _set_field(self, field: Union["TagChecker", HtmlTagAttribute], field_name: str) -> None:
        self._fields[field_name] = field
        setattr(self, field_name, field)
        field.bind(root=self, field_name=field_name)

    def bind(self, root: "TagChecker", field_name: str) -> None:
        self.root = root
        self.field_name = field_name

    def fill(self) -> None:
        self._find_elem()
        if self.elem is not None:
            self._bind_fields()
            self._fill_attributes()
            self._fill_childrens()

    def _find_elem(self) -> None:
        if hasattr(self, GET_ELEMENT_METHOD_NAME):
            get_element_method = getattr(self, GET_ELEMENT_METHOD_NAME)
            element = get_element_method()
            if not (isinstance(element, Tag) or element is None):
                raise TypeError(f"{GET_ELEMENT_METHOD_NAME} method must return bs4.Tag type, not {type(element)}")
            self.elem = element
            return
        if self.elem:
            return
        if self.selector:
            self.elem = self.root.elem.select_one(self.selector)
            return
        raise AttributeError(f'Set "elem", "selector", or define "{GET_ELEMENT_METHOD_NAME}" method in your class')

    def _fill_attributes(self) -> None:
        for attribute_field_name, attribute in self.attributes.items():
            with contextlib.suppress(KeyError):
                attribute_value = self.elem[attribute.name]
                if isinstance(attribute_value, AttributeValueList):
                    attribute_value = " ".join(attribute_value)
                attribute.value = attribute_value

    def _fill_childrens(self) -> None:
        for child_name, children in self.childrens.items():
            children.fill()

    def exist(self) -> bool:
        return bool(self.elem)

    @property
    def attributes(self) -> dict[str, HtmlTagAttribute]:
        return {field_name: field for field_name, field in self._fields.items() if isinstance(field, HtmlTagAttribute)}

    @property
    def childrens(self) -> dict[str, "TagChecker"]:
        return {field_name: field for field_name, field in self._fields.items() \
                if isinstance(field, (TagChecker, ListTagChecker))}

    def get_short_display(self) -> str:
        if self.elem:
            return f"<{self.elem.name} {self.elem.attrs}>...</{self.elem.name}>"
        return ""

    @property
    def tag_name(self) -> str:
        if self.elem:
            return self.elem.name
        if self.selector:
            return self.selector
        return self.__class__.__name__

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
        field_validation_method = self._get_custom_field_validator(field_name=field_name)
        if field_validation_method is not None:
            field = getattr(self, field_name)
            try:
                field_validation_method(field=field)
            except ValidationError as error:
                if isinstance(field,TagChecker):
                    field.errors.setdefault(NON_FIELD_ERROR, []).append(error)
                elif isinstance(field, ListTagChecker):
                    self.errors.setdefault(NON_FIELD_ERROR, []).append(error)
                elif isinstance(field, HtmlTagAttribute):
                    field.errors.append(error)
                else:
                    raise TypeError(f"Unknown class type of field {type(field)}")

    def _required_validation(self) -> None:
        if self.required and self.elem is None:
            raise ValidationError(
                message=f"{self.tag_name} required",
                level=self.DEFAULT_ERROR_LEVEL,
            )

    def validate(self) -> None:
        """Hook"""


class ListTagChecker:
    DEFAULT_ERROR_LEVEL = levels.ERROR

    def __init__(self, field: TagChecker):
        self.field = field
        self.many = True
        self.root = None
        self.field_name = None
        self.tags_items = []
        self.errors = []

    def __iter__(self):
        return iter(self.tags_items)

    def __len__(self):
        return len(self.tags_items)

    def exist(self) -> bool:
        return bool(self.tags_items)

    def bind(self, root: "TagChecker", field_name: str) -> None:
        self.root = root
        self.field_name = field_name

    def fill(self) -> None:
        elements = self.root.elem.select(self.field.selector)
        for elem_number, elem in enumerate(elements):
            field = deepcopy(self.field)
            field.elem = elem
            field.elem_number = elem_number + 1
            field.root = self.root
            self.tags_items.append(field)
            field.fill()

    def run_validators(self) -> None:
        try:
            self._required_validation()
        except ValidationError as error:
            self.root.errors.setdefault(NON_FIELD_ERROR, []).append(error)
            return
        for field in self.tags_items:
            field.run_validators()
        for field in self.tags_items:
            self.errors.append(field.errors)

    def _required_validation(self) -> None:
        if self.field.required and len(self.tags_items) == 0:
            raise ValidationError(
                f"Must provide at least one item: {self.field.path_name}",
                level=self.DEFAULT_ERROR_LEVEL,
            )

class HtmlTag(TagChecker):
    def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
        elem = kwargs.get("elem")
        if not isinstance(elem, Tag):
            raise TypeError("Expected bs4.Tag for 'elem'")
        if elem.name != "html":
            raise ValueError(f"Expected <html> tag, got <{elem.name}>")
        super().__init__(
            *args,
            many=False,
            root=None,
            required=True,
            selector="html",
            **kwargs,
        )
        self.fill()
