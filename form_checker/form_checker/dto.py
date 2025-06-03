from collections import OrderedDict
from dataclasses import dataclass

from html_checker import TagChecker


@dataclass
class HtmlCheckResult:
    preset: TagChecker
    errors_level_stat: OrderedDict
