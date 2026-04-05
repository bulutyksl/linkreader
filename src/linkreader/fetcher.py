from __future__ import annotations

import time

import trafilatura
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class FetchError(Exception):
    pass


class Fetcher:
    def __init__(self, delay: float = 2.0, max_retries: int = 3):
        self.delay = delay
        self.max_retries = max_retries
        self._last_request_time = 0.0

        # Build the retry-wrapped fetch method dynamically based on max_retries
        self._fetch_with_retry = retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=4, max=30),
            retry=retry_if_exception_type(FetchError),
            reraise=True,
        )(self._do_fetch)

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request_time = time.time()

    def _do_fetch(self, url: str) -> str:
        self._rate_limit()
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            raise FetchError(f"Failed to fetch {url}")
        return downloaded

    def fetch(self, url: str) -> str:
        return self._fetch_with_retry(url)
