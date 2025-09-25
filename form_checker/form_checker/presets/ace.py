from html_checker import HtmlTag, HtmlTagAttribute, TagChecker, levels
from html_checker.exceptions import ValidationError


class FirstNameInput(TagChecker):
    SELECTOR = "input[name=first_name]"
    type = HtmlTagAttribute(expected="text")
    pattern = HtmlTagAttribute(expected="[A-Za-z\s\-]{2,}")
    required = HtmlTagAttribute()


class LastNameInput(TagChecker):
    SELECTOR = "input[name=last_name]"
    type = HtmlTagAttribute(expected="text")
    pattern = HtmlTagAttribute(expected="[A-Za-z\s\-]{2,}")
    required = HtmlTagAttribute()


class EmailInput(TagChecker):
    SELECTOR = "input[name=email]"
    type = HtmlTagAttribute(expected="email")
    required = HtmlTagAttribute()



class PasswordInput(TagChecker):
    SELECTOR = "input[name=password]"
    type = HtmlTagAttribute(expected="text")
    required = HtmlTagAttribute()

class PhoneCcValue(HtmlTagAttribute):

    def validate(self) -> None:
        raise ValidationError(self.value, level=levels.INFO)

class PhoneCCInput(TagChecker):
    SELECTOR = "input[name=phonecc]"
    type = HtmlTagAttribute(expected="hidden")
    value = PhoneCcValue()

class Form(TagChecker):
    action = HtmlTagAttribute(choices=("send.php", "./send.php"))

    aff_sub = TagChecker(
        selector="input[name=aff_sub]",
        attributes={"type": {"expected": "hidden"}, "value": {"expected": "{subid}"}},
    )
    user_agent = TagChecker(
        selector="input[name=ua]",
        attributes={"type": {"expected": "hidden"}, "value": {"expected": "{_user_agent}"}},
    )
    ip_address = TagChecker(
        selector="input[name=ip]",
        attributes={"type": {"expected": "hidden"}, "value": {"expected": "{ip}"}},
    )
    phone_cc = PhoneCCInput()
    first_name = FirstNameInput()
    last_name = LastNameInput()
    email = EmailInput()
    phone = TagChecker(selector="input[name=phone]", attributes={"type": {"expected": "tel"}})
    password = PasswordInput()


class AceAffHtml(HtmlTag):
    order_form = Form(selector="form", many=True)
