from collections import OrderedDict
from collections.abc import Mapping

from html_checker import HtmlTagAttribute, ListTagChecker, TagChecker

from .exceptions import ValidationError
from .levels import ERROR, INFO, SUCCESS, WARNING, ErrorLevel


def convert_errors(err: dict) -> dict | list | str:
    if isinstance(err, list):
        return [convert_errors(e) for e in err]
    if isinstance(err, ValidationError):
        return err.to_detail()
    if isinstance(err, dict):
        return {k: convert_errors(v) for k, v in err.items()}
    return str(err)


def convert_to_dict(elem):
    if isinstance(elem, ListTagChecker):
        return [convert_to_dict(item) for item in elem.items]

    if isinstance(elem, TagChecker):
        return {
            "name": elem.name,
            "class_name": elem.__class__.__name__,
            "elem_number": elem.elem_number,
            "type": "Tag",
            "get_short_display": elem.get_short_display(),
            "exist": bool(elem.elem),
            "errors": convert_errors(elem.errors),
            "children": {field_name: convert_to_dict(field) for field_name, field in elem.childrens.items()}
            if elem.childrens.items()
            else None,
            "attrs": {attr_name: convert_to_dict(attr) for attr_name, attr in elem.attributes.items()}
            if elem.attributes.items()
            else None,
        }

    if isinstance(elem, HtmlTagAttribute):
        return {
            "name": elem.name,
            "type": "attribute",
            "value": elem.value,
            "expected": elem.expected,
            "choices": elem.choices,
            "errors": convert_errors(elem.errors),
        }

    return {"1": "1"}


def get_errors_levels_stat(tag: TagChecker) -> OrderedDict[ErrorLevel, int]:
    result = OrderedDict(
        [
            (SUCCESS, 0),
            (INFO, 0),
            (WARNING, 0),
            (ERROR, 0),
        ],
    )

    def collect_errors(error_collection: list | Mapping) -> None:
        if isinstance(error_collection, Mapping):
            for key, value in error_collection.items():
                collect_errors(error_collection=value)
        elif isinstance(error_collection, list):
            for error_item in error_collection:
                if isinstance(error_item, ValidationError):
                    result[error_item.level] += 1
                elif isinstance(error_item, Mapping):
                    collect_errors(error_collection=error_item)
                else:
                    raise TypeError(f"Incorrect error collection type: {type(error_collection)}")
        else:
            raise TypeError(f"Incorrect error collection type: {type(error_collection)}")

    collect_errors(tag.errors)
    return result
