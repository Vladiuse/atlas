import re
from html_checker import HtmlTagAttribute, TagChecker, levels
from html_checker.exceptions import ValidationError

class Title(TagChecker):
    def validate(self) -> None:
        if self.exist() and self.elem.text == "Document":
            raise ValidationError("Неправильный текст в title")


class Sub21Input(TagChecker):
    SELECTOR = "input[name=sub_id_21]"
    DEFAULT_ERROR_LEVEL = levels.WARNING
    autocomplete = HtmlTagAttribute(expected="address-level2")


class Sub22Input(TagChecker):
    SELECTOR = "input[name=sub_id_22]"
    DEFAULT_ERROR_LEVEL = levels.WARNING
    autocomplete = HtmlTagAttribute(expected="street-address")


class Sub23Input(TagChecker):
    SELECTOR = "input[name=sub_id_23]"
    DEFAULT_ERROR_LEVEL = levels.WARNING
    autocomplete = HtmlTagAttribute(expected="postal-code")


class Sub9Select(TagChecker):
    SELECTOR = "select[name=sub_id_9]"
    DEFAULT_ERROR_LEVEL = levels.INFO
    autocomplete = HtmlTagAttribute(expected="address-level1")


class Sub24Input(TagChecker):
    SELECTOR = "input[name=sub_id_24]"
    autocomplete = HtmlTagAttribute(expected="given-name")


class Sub25Input(TagChecker):
    SELECTOR = "input[name=sub_id_25]"
    autocomplete = HtmlTagAttribute(expected="family-name")


class Sub26Input(TagChecker):
    SELECTOR = "input[name=sub_id_26]"
    autocomplete = HtmlTagAttribute(expected="tel-national")


class Sub27Input(TagChecker):
    SELECTOR = "input[name=sub_id_27]"
    autocomplete = HtmlTagAttribute(expected="email")


class OrderForm(TagChecker):
    id = HtmlTagAttribute(expected="mForm")
    sub_id_24 = Sub24Input()
    sub_id_25 = Sub25Input()
    sub_id_26 = Sub26Input()
    sub_id_27 = Sub27Input()

    sub_id_21 = Sub21Input()
    sub_id_22 = Sub22Input()
    sub_id_23 = Sub23Input()

    sub_id_9 = Sub9Select()


class JsFuncDetector(TagChecker):
    """Чекер для поиска наличия js функции к коде index.html"""
    FUNCTION_NAME_TO_SEARCH = None

    def validate(self) -> None:
        if self.FUNCTION_NAME_TO_SEARCH is None:
            raise AttributeError('Set FUNCTION_NAME_TO_SEARCH')
        scripts = self.root.elem.select("script")
        is_func_exist = False
        for script in scripts:
            pattern = rf"function[\t ]+{re.escape(self.FUNCTION_NAME_TO_SEARCH)}[\t ]*\("
            if re.search(pattern, script.text):
                is_func_exist = True
                break
        if not is_func_exist:
            raise ValidationError(f"Функция {self.FUNCTION_NAME_TO_SEARCH} не найдена", level=levels.WARNING)


class GetShortImageSrcDetector(JsFuncDetector):
    FUNCTION_NAME_TO_SEARCH = "getShortImageSrc"
    SELECTOR = "script-getShortImageSrc"

class InjectScriptDetector(JsFuncDetector):
    FUNCTION_NAME_TO_SEARCH = "injectScript"
    SELECTOR = "script-injectScript"


class AtlasHtml(TagChecker):
    title = Title(selector="title")
    form = OrderForm(selector="form", many=True)
    short_img_script = GetShortImageSrcDetector(required=False)
    inject_script = InjectScriptDetector(required=False)
