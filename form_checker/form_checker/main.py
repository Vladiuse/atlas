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
    def __init__(self, elem: Tag, name: str, prefix: str = ""):
        self._name = name
        self.prefix = prefix
        self.elem = elem
        self.errors = []

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
    def check_method(self) -> None:
        if not self._attr_value_eq("action", "POST", ignore_case=True):
            raise ValidationError(message="incorrect action value", level=ERROR)

    def check_id(self) -> None:
        if not self._attr_value_eq("id", "mForm"):
            raise ValidationError(message="Incorrect form id", level=ERROR)

    def check_phone_input(self) -> None:
        phone_input = self.elem.select_one("input[name=phone]")
        if not phone_input:
            raise ValidationError(message="Phone input not found")
        phone_checker = PhoneInputChecker(elem=phone_input, name="phone_input", prefix=self._name)
        phone_checker.run_checks()
        self.errors.extend(phone_checker.errors)


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
