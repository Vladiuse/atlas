from typing import Optional
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from .exceptions import FormNotFound

SUCCESS = "success"
WARNING = "warning"
ERROR = "danger"


@dataclass
class Error:
    check_name: str
    message: str
    level: str
    elem: str | None


@dataclass
class ValidationError(Exception):
    message: str
    level: str = ERROR


class TagChecker:
    def __init__(
        self,
        name: str,
        elem: Tag | None = None,
        selector: str | None = None,
        prefix: str = "",
        root: Optional["TagChecker"] = None,
    ):
        self._name = name
        self.selector = selector
        self._root = root
        self.prefix = prefix
        self._elem = elem
        self.errors = []

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value

    def _get_nested_tags(self) -> list['TagChecker']:
        tags = []
        for name in dir(self):
            checker = getattr(self, name)
            if name not in ['root', '_root'] and isinstance(checker, TagChecker):
                checker.root = self
                elem =  self.elem.select_one(checker.selector)
                checker.elem =elem
                tags.append(checker)
        return tags

    @property
    def elem(self) -> Tag:
        return self._elem

    @elem.setter
    def elem(self, value):
        self._elem = value

    @property
    def name(self) -> str:
        if self.prefix:
            return f"{self.prefix}_{self._name}"
        return self._name

    def _attr_value_eq(self, attr_name: str, value: str, *, ignore_case: bool = False) -> bool:
        try:
            attr_value = self.elem[attr_name]
            if ignore_case is True:
                return attr_value.lower() == value.lower()
            return attr_value == value
        except KeyError:
            return False

    def _get_checks_methods(self) -> list:
        methods = []
        for name in dir(self):
            if name.startswith("check_"):
                method = getattr(self, name)
                if callable(method):
                    methods.append(method)
        return methods

    # def check(self):
    #     pass

    def run_checks(self) -> None:
        self.run_methods_checks()
        self.run_nested_checks()

    def run_nested_checks(self) -> None:
        nested_tags = self._get_nested_tags()
        for nested_checker in nested_tags:
            if nested_checker.elem is None:
                error = Error(
                    check_name=f"{self.name}.{nested_checker.__class__.__name__}",
                    message=f"{nested_checker.selector} not found",
                    level=ERROR,
                    elem='',
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
                    check_name=f"{self.name}.{checker.__name__}",
                    message=e.message,
                    level=e.level,
                    elem=str(self.elem),
                )
                self.errors.append(error)


class PhoneInputChecker(TagChecker):
    def check_type(self) -> None:
        if not self._attr_value_eq(attr_name="type", value="tel"):
            raise ValidationError("Incorrect type attr")


class FormChecker(TagChecker):

    phone_input = PhoneInputChecker(selector='input[name=phone]', name='phone_input')

    def check_method(self) -> None:
        if not self._attr_value_eq("action", "POST", ignore_case=True):
            raise ValidationError(message="incorrect action value", level=ERROR)

    def check_id(self) -> None:
        if not self._attr_value_eq("id", "mForm"):
            raise ValidationError(message="Incorrect form id", level=ERROR)


class HtmlChecker:
    def check(self, html: str) -> list[Error]:
        errors = []
        soup = BeautifulSoup(html, "lxml")
        forms = self._find_forms(soup=soup)
        for form_number, form in enumerate(forms):
            form_checker = FormChecker(elem=form, name=f"form_{form_number + 1}")
            form_checker.run_checks()
            errors.extend(form_checker.errors)
        return errors

    def _find_forms(self, soup: BeautifulSoup) -> list[Tag]:
        forms = soup.findAll("form")
        if len(forms) == 0:
            raise FormNotFound("Не найдена ни одна форма")
        return forms
