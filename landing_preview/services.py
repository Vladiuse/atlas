import requests
from django.conf import settings
from requests.exceptions import HTTPError, RequestException

from landing_preview.exceptions import AppExtension

KEITARO_LANDING_DETAIL_URL = "https://mrbrw.com/admin_api/v1/landing_pages/"


def get_keitaro_landing_api_data(landing_id: str) -> dict:
    headers = {"Authorization": f"Bearer {settings.KEITARO_TOKEN}", "Content-Type": "application/json"}
    try:
        response = requests.get(url=KEITARO_LANDING_DETAIL_URL + landing_id, headers=headers)
        response.raise_for_status()
        return response.json()
    except HTTPError:
        message = f"Keitaro error: {response.status_code}: {response.text}"
        raise AppExtension(message)
    except RequestException as error:
        message = f"Keitaro request error: {error}"
        raise AppExtension(message)


def load_html_from_url(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except HTTPError:
        message = f"Get index page error: {response.status_code}: {response.text}"
        raise AppExtension(message)
    except RequestException as error:
        message = f"Get index page error: {error}"
        raise AppExtension(message)
