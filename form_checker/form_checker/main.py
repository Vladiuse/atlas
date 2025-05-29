from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from .exceptions import FormNotFound

SUCCESS = "success"
WARNING = "warning"
ERROR = "danger"


@dataclass
class CheckResult:
    name: str
    status: str
    message: str = ""
    prefix: str = ""


class FormChecker:
    def __init__(self, elem: Tag, form_number_on_page: int):
        self.form_number_on_page = form_number_on_page
        self.elem = elem

    def check(self) -> list[CheckResult]:
        check_results = []
        check_funcs_list = [
            self._check_method,
            self._check_action,
            self._check_name_input,
            self._check_phone_input,
        ]

        for check_func in check_funcs_list:
            result = check_func()
            result.prefix = f'form-{self.form_number_on_page}'
            check_results.append(result)
        return check_results

    def _attr_value_eq(self, attr_name: str, value: str, *, ignore_case: bool = False) -> bool:
        try:
            attr_value = self.elem[attr_name]
            if ignore_case is True:
                return attr_value.lower() == value.lower()
            return attr_value == value
        except KeyError:
            return False

    def _check_name_input(self) -> CheckResult:
        name = 'name_input'
        input_name = self.elem.select_one('input[name="name"]')
        if input_name:
            return CheckResult(
                name=name,
                status=SUCCESS,
            )
        return CheckResult(
            name=name,
            status=ERROR,
            message='Инпут имени не найден',
        )

    def _check_phone_input(self) -> CheckResult:
        name = 'phone_input'
        phone_input = self.elem.select_one('input[name="phone"]')
        if phone_input:
            return CheckResult(
                name=name,
                status=SUCCESS,
            )
        return CheckResult(
            name=name,
            status=ERROR,
            message='Инпут номера телефона не найден',
        )

    def _check_method(self) -> CheckResult:
        check_name = "form_method=POST"
        if self._attr_value_eq(attr_name="method", value="post", ignore_case=True):
            return CheckResult(
                name=check_name,
                status=SUCCESS,
            )
        return CheckResult(
            name=check_name,
            status=ERROR,
            message="Метод формы должен быть POST",
        )

    def _check_action(self) -> CheckResult:
        check_name = "form_check_action"
        if self._attr_value_eq(attr_name="action", value="order.php"):
            return CheckResult(
                name=check_name,
                status=SUCCESS,
            )
        return CheckResult(
            name=check_name,
            status=ERROR,
            message="Неправильная ссылка на оффер",
        )


class HtmlChecker:

    def check(self, html: str) -> list[CheckResult]:
        result = []
        soup = BeautifulSoup(html, "lxml")
        forms = self._find_forms(soup=soup)
        for form_number, form in enumerate(forms):
            form_checker = FormChecker(elem=form, form_number_on_page=form_number + 1)
            check_results = form_checker.check()
            result.extend(check_results)
        return result

    def _find_forms(self, soup: BeautifulSoup) -> list[Tag]:
        forms = soup.findAll("form")
        if len(forms) == 0:
            raise FormNotFound("Не найдена ни одна форма")
        return forms
