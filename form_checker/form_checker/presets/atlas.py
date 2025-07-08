from bs4 import Tag

from html_checker import HtmlTag, HtmlTagAttribute, TagChecker, levels
from html_checker.exceptions import ValidationError
from html_checker.utils import find_script_with_js_function


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


class GetShortImageSrcDetector(TagChecker):
    SELECTOR = "script with getShortImageSrc"

    def get_element(self) -> Tag | None:
        scripts = self.root.elem.select("script")
        return find_script_with_js_function(scripts=scripts, js_function_name="getShortImageSrc")


class InjectScriptDetector(TagChecker):
    SELECTOR = "script with injectScript"

    def get_element(self) -> Tag | None:
        scripts = self.root.elem.select("script")
        return find_script_with_js_function(scripts=scripts, js_function_name="injectScript")


class AtlasHtml(HtmlTag):
    title = Title(selector="title")
    form = OrderForm(selector="form", many=True)
    short_img_script = GetShortImageSrcDetector()
    inject_script = InjectScriptDetector()

    header_logo_img = TagChecker(selector="img.def-product-item-image")
    default_product_img = TagChecker(selector="img.header_9__logo")
