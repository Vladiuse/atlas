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
        not_exist_error_level: str = ERROR,
    ):
        self._name = name
        self.selector = selector
        self._root = root
        self.prefix = prefix
        self._elem = elem
        self.errors = []
        self.not_exist_error_level = not_exist_error_level

    def get_short_display(self) -> str:
        return f"<{self.elem.name} {self.elem.attrs}>...</{self.elem.name}>"

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
    def elem(self, value: Tag) -> Tag | None:
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
                    level=nested_checker.not_exist_error_level,
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
                    elem=self.get_short_display(),
                )
                self.errors.append(error)


class PhoneInputChecker(TagChecker):
    def check_type(self) -> None:
        if not self._attr_value_eq(attr_name="type", value="tel"):
            raise ValidationError("Incorrect type attr")


class NameInput(TagChecker):

    def check_type(self) -> None:
        if not self._attr_value_eq(attr_name="type", value="text"):
            raise ValidationError("Incorrect type attr", level=WARNING)


class Sub24Input(TagChecker):

    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "given-name"
        if not self._attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")

class Sub25Input(TagChecker):

    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "family-name"
        if not self._attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")

class Sub26Input(TagChecker):

    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "tel-national"
        if not self._attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")

class Sub27Input(TagChecker):

    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "email"
        if not self._attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")

# Необязательно, но желательно:
# name="sub_id_22" && autocomplete="street-address"
# name="sub_id_23" && autocomplete="postal-code"
# name="sub_id_21" && autocomplete="address-level2"

class Sub22Input(TagChecker):

    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "street-address"
        if not self._attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")

class Sub23Input(TagChecker):

    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "postal-code"
        if not self._attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")


class Sub21Input(TagChecker):
    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "address-level2"
        if not self._attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")


class FormChecker(TagChecker):

    phone_input = PhoneInputChecker(selector='input[name=phone]', name='phone_input')
    name_input = NameInput(selector='input[name=name]', name='name_input')
    sub_24 = Sub24Input(selector='input[name=sub_id_24]', name='sub_24')
    sub_25 = Sub25Input(selector='input[name=sub_id_25]', name='sub_25')
    sub_26 = Sub26Input(selector='input[name=sub_id_26]', name='sub_26')
    sub_27 = Sub27Input(selector='input[name=sub_id_27]', name='sub_27')
    sub_22 = Sub22Input(selector='input[name=sub_id_22]', name='sub_22', not_exist_error_level=WARNING)
    sub_23 = Sub22Input(selector='input[name=sub_id_23]', name='sub_23', not_exist_error_level=WARNING)
    sub_21 = Sub22Input(selector='input[name=sub_id_21]', name='sub_21', not_exist_error_level=WARNING)

    def check_method(self) -> None:
        if not self._attr_value_eq("method", "POST", ignore_case=True):
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
