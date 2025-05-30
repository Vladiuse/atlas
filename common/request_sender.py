import logging
from typing import Any

import requests
from requests.exceptions import RequestException


class RequestSender:
    def request(self, url: str, attempts: int = 2, method: str = 'GET', **kwargs: dict[str, Any]) -> str:
        if attempts <= 0:
            raise ValueError('attempts must be positive integer')
        last_error = None
        for _ in range(attempts):
            try:
                response = requests.request(url=url, method=method, timeout=10, **kwargs)
                logging.info('%s: %s', response.status_code, url)
                response.raise_for_status()
                return response.text
            except RequestException as error:
                last_error = error
        raise last_error