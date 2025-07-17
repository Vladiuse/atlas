import re

from .constants import KEITARO_URL


def get_keitaro_index_file_url(landing_local_path: str) -> str:
    return KEITARO_URL + landing_local_path


def add_or_change_tag_base_href(html: str, new_href: str) -> str:
    new_base_tag = f'<base href="{new_href}">'
    result = re.search(r"<base\b[^>]*>", html)
    return re.sub("<base\\b[^>]*>", new_base_tag, html) if result else new_base_tag + html


def render_keitaro_landing_html(html: str, base_url: str, context: dict[str, str]) -> str:
    html = add_or_change_tag_base_href(new_href=base_url, html=html)
    for var_template, value in context.items():
        html = html.replace(var_template, value)
    return html