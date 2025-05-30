from bs4 import BeautifulSoup, Tag

from html_checker.constants import ERROR, WARNING
from html_checker.dto import Error
from html_checker.exceptions import FormNotFound, ValidationError
from html_checker.fields import TagChecker


class PhoneInputChecker(TagChecker):
    def check_type(self) -> None:
        if not self.attr_value_eq(attr_name="type", value="tel"):
            raise ValidationError("Incorrect type attr")


class NameInput(TagChecker):
    def check_type(self) -> None:
        if not self.attr_value_eq(attr_name="type", value="text"):
            raise ValidationError("Incorrect type attr", level=WARNING)


class Sub24Input(TagChecker):
    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "given-name"
        if not self.attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")


class Sub25Input(TagChecker):
    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "family-name"
        if not self.attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")


class Sub26Input(TagChecker):
    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "tel-national"
        if not self.attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")


class Sub27Input(TagChecker):
    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "email"
        if not self.attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")


class Sub22Input(TagChecker):
    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "street-address"
        if not self.attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")


class Sub23Input(TagChecker):
    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "postal-code"
        if not self.attr_value_eq(attr_name=attr_to_check, value=value):
            raise ValidationError(f"Incorrect attr {attr_to_check}")


class Sub21Input(TagChecker):
    def check_autocomplete(self) -> None:
        attr_to_check = "autocomplete"
        value = "address-level2"
        if not self.attr_value_eq(attr_name=attr_to_check, value=value):
            current_value = self.get_attr_value(attr_name=attr_to_check)
            raise ValidationError(f"Incorrect attr {attr_to_check}, current value: {current_value}")


class AtlasFormChecker(TagChecker):
    sub_24 = Sub24Input(selector='input[name=sub_id_24]', name='sub_24')
    sub_25 = Sub25Input(selector='input[name=sub_id_25]', name='sub_25')
    sub_26 = Sub26Input(selector='input[name=sub_id_26]', name='sub_26')
    sub_27 = Sub27Input(selector='input[name=sub_id_27]', name='sub_27')
    sub_22 = Sub22Input(selector='input[name=sub_id_22]', name='sub_22', not_exist_error_level=WARNING)
    sub_23 = Sub23Input(selector='input[name=sub_id_23]', name='sub_23', not_exist_error_level=WARNING)
    sub_21 = Sub21Input(selector='input[name=sub_id_21]', name='sub_21', not_exist_error_level=WARNING)


    def check_id(self) -> None:
        if not self.attr_value_eq("id", "mForm"):
            raise ValidationError(message="Incorrect form id", level=ERROR)


class HtmlChecker:
    def check(self, html: str) -> list[Error]:
        errors = []
        soup = BeautifulSoup(html, "lxml")
        forms = self._find_forms(soup=soup)
        for form_number, form in enumerate(forms):
            form_checker = AtlasFormChecker(elem=form, name=f"form_{form_number + 1}")
            form_checker.run_checks()
            errors.extend(form_checker.errors)
        return errors

    def _find_forms(self, soup: BeautifulSoup) -> list[Tag]:
        forms = soup.findAll("form")
        if len(forms) == 0:
            raise FormNotFound("Не найдена ни одна форма")
        return forms
