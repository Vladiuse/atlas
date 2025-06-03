import json
from common.constants import ATLAS_TEAM
from bs4 import BeautifulSoup, Tag

from common.request_sender import RequestSender
from .presets import PRESETS_MAP
from html_checker.utils import get_errors_levels_stat
from .exceptions import HtmlTagNotFound
from .dto import HtmlCheckResult

request_sender = RequestSender()





class HtmlChecker:

    def __init__(self, request_sender: RequestSender):
        self.request_sender = request_sender

    def check(self, html: str, preset_name: str, url: str) -> HtmlCheckResult:
        if url != '':
            html = self.request_sender.request(url=url)
        soup = BeautifulSoup(html, "lxml")
        html_tag = soup.select_one('html')
        if html_tag is None:
            raise HtmlTagNotFound('Не найден корневой тэг <html>')
        preset = PRESETS_MAP[preset_name]
        html_preset = preset(elem=html_tag)
        html_preset.run_validators()
        errors_level_stat = get_errors_levels_stat(tag=html_preset)
        return HtmlCheckResult(
            preset=html_preset,
            errors_level_stat=errors_level_stat,
        )
