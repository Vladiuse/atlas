from bs4 import BeautifulSoup

from html_checker import HtmlTagAttribute, TagChecker
from html_checker.exceptions import ValidationError
from html_checker.levels import INFO, SUCCESS, WARNING


class Title(TagChecker):
    _class = HtmlTagAttribute(name="class", expected="title_id some")


class TypeAttr(HtmlTagAttribute):
    def validate(self):
        raise ValidationError("NAME NAME", level=SUCCESS)


class PhoneInput(TagChecker):
    name = HtmlTagAttribute(expected="name")
    type = TypeAttr(expected="tel")

    def validate(self):
        raise ValidationError("phone", level=WARNING)

    def validate_name(self, field):
        raise ValidationError("phone name", level=WARNING)


class Form(TagChecker):
    id = HtmlTagAttribute(expected="MyId")
    phone = PhoneInput(selector="input[name=phone]")

    def validate(self):
        raise ValidationError("FORM validate")

    def validate_id(self, field):
        raise ValidationError("FOrm field error", level=INFO)


class TestHtml(TagChecker):
    lang = HtmlTagAttribute(expected="ru")
    title = Title(selector="title")
    form = Form(selector="form", many=True)


if __name__ == "__main__":
    with open("/home/vlad/PycharmProjects/atlas/test.html") as file:
        html = file.read()
    soup = BeautifulSoup(html, "lxml")
    html_tag = TestHtml(elem=soup.select_one("html"))
    html_tag.run_validators()
    print(html_tag.form)
    for form in html_tag.form:
        print(type(form.phone), form.phone.path_name, form.phone.selector, form.phone.elem)
