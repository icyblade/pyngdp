import requests
from cachecontrol import CacheControlAdapter
from cachecontrol.heuristics import ExpiresAfter
from urllib3.util.retry import Retry

from .binary_stream import BinaryStream

USER_AGENT = 'pyngdp/1.0'


class Session(object):
    def __init__(self, max_retries=5, timeout=5):
        self._build_session(max_retries)
        self.timeout = timeout

    def _build_session(self, max_retries):
        from requests.adapters import HTTPAdapter

        if not isinstance(max_retries, int):
            raise ValueError(f'int expected, found {type(max_retries)}.')
        elif max_retries < 1:
            raise ValueError('max_retries should be greater or equal to 1.')

        session = requests.Session()

        # mount retries adapter
        session.mount('http://', HTTPAdapter(max_retries=Retry(
            total=max_retries, method_whitelist=frozenset(['GET', 'POST'])
        )))

        # mount cache adapter
        session.mount('http://', CacheControlAdapter(heuristic=ExpiresAfter(hours=1)))

        session.headers['User-Agent'] = USER_AGENT

        self.session = session

    def _get(self, *args, **kwargs):
        kwargs['timeout'] = self.timeout
        r = self.session.get(*args, **kwargs)
        return r

    def get_text(self, *args, **kwargs):
        text = self._get(*args, **kwargs).text
        return text

    def get_binary(self, *args, **kwargs):
        from io import BytesIO
        content = self._get(*args, **kwargs).content

        return BinaryStream(BytesIO(content))
