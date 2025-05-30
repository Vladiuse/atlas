from common.constants import ATLAS_TEAM
from html_checker.dto import Error
from bs4 import BeautifulSoup, Tag
from html_checker.exceptions import FormNotFound
from common.request_sender import RequestSender
from .atlas import AtlasFormChecker

request_sender = RequestSender()
def get_checker_by_team(team: str) -> type[AtlasFormChecker]:
    return  {ATLAS_TEAM: AtlasFormChecker}[team]


class HtmlChecker:
    def check(self, html: str, team: str, url: str) -> list[Error]:
        if url != '':
            html = request_sender.request(url=url)
        with open('req.html', 'w') as file:
            file.write(html)
        checker_class = get_checker_by_team(team=team)
        errors = []
        soup = BeautifulSoup(html, "lxml")
        forms = self._find_forms(soup=soup)
        for form_number, form in enumerate(forms):
            form_checker = checker_class(elem=form, name=f"form_{form_number + 1}")
            form_checker.run_checks()
            errors.extend(form_checker.errors)
        return errors

    def _find_forms(self, soup: BeautifulSoup) -> list[Tag]:
        forms = soup.findAll("form")
        if len(forms) == 0:
            raise FormNotFound("Не найдена ни одна форма")
        return forms
