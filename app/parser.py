import logging
import re
from threading import Thread
from typing import List
import unicodedata

from bs4 import BeautifulSoup
import requests


logger = logging.getLogger(__name__)


def get_files(url: str) -> List[dict]:
    url = url.replace('/details/', '/download/')
    url = url[:-1] if url.endswith('/') else url

    try:
        content = requests.get(url).text
        html = BeautifulSoup(content, features='html.parser')
        links = html.select('table.directory-listing-table td > a:first-child')
        sizes = html.select('table.directory-listing-table tr > td:nth-child(3)')

        if len(links) < 1:
            return []

        files = []
        for i in range(1, len(links[1:])):
            row = links[i]
            files.append({
                'url': f"{url}/{row['href']}",
                'filename': row.text,
                'size': sizes[i].text,
            })

        return files
    except Exception as e:
        logger.exception(f'Failed to get page: {e}')
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
        self.files = []

    def run(self):
        self.files = get_files(self.url)
