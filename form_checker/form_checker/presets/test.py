from html_checker import HtmlTag, HtmlTagAttribute, TagChecker
from html_checker.exceptions import ValidationError


class Title(TagChecker):
    _class = HtmlTagAttribute(name="class", expected="title_class")


class PhoneInput(TagChecker):
    name = HtmlTagAttribute(expected="phone")
    type = HtmlTagAttribute(expected="tel")


class Form(TagChecker):
    id = HtmlTagAttribute(expected="MyId")
    phone = PhoneInput(selector="input[name=phone]")
    button = TagChecker(selector="button", attributes={"type": {"expected": "submit"}})


class TestHtml(HtmlTag):
    lang = HtmlTagAttribute(expected="en")
    # title = Title(selector="title")
    form = Form(selector="form", many=True)

    def validate(self):
        raise ValidationError("123")
