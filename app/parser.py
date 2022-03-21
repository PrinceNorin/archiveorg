import logging
import re
from threading import Thread
from typing import List
import unicodedata

from bs4 import BeautifulSoup
import requests


logger = logging.getLogger(__name__)


def get_files(url: str) -> List[str]:
    url = url.replace('/details/', '/download/')
    url = url[:-1] if url.endswith('/') else url

    try:
        content = requests.get(url).text
        html = BeautifulSoup(content, features='html.parser')
        rows = html.select('table.directory-listing-table a')

        if len(rows) < 1:
            return []

        return [f"{url}/{row['href']}" for row in rows[1:]]
    except Exception as e:
        logger.exception(f'Failed to get page: {e}', err=e)
        return []


def slugify_from_url(url):
    return slugify(url.split('/')[-1])


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


class AsyncFetchFile(Thread):
    def __init__(self, url):
        super().__init__()

        self.url = url
        self.urls = []

    def run(self):
        self.urls = get_files(self.url)
