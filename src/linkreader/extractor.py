from __future__ import annotations

import re
from typing import Any

import trafilatura

DATE_IN_URL_RE = re.compile(r"/(20[12]\d)/(\d{2})/(\d{2})/")


def extract_article(html: str, url: str) -> dict[str, Any]:
    text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
        deduplicate=True,
        target_language="tr",
    )

    doc = trafilatura.bare_extraction(html, url=url)

    date = getattr(doc, "date", None)
    if not date:
        date = _date_from_url(url)

    return {
        "text": text,
        "title": getattr(doc, "title", None),
        "author": getattr(doc, "author", None),
        "date": date,
        "sitename": getattr(doc, "sitename", None),
    }


def _date_from_url(url: str) -> str | None:
    m = DATE_IN_URL_RE.search(url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None
