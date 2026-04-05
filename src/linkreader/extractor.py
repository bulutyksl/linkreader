from __future__ import annotations

import re
from typing import Any

import trafilatura

DATE_IN_URL_RE = re.compile(r"/(2\d{3})/(\d{2})/(\d{2})/")


def extract_article(html: str, url: str) -> dict[str, Any]:
    doc = trafilatura.bare_extraction(
        html,
        url=url,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
        deduplicate=True,
        target_language="tr",
    )

    if doc is None:
        return {"text": None, "title": None, "author": None, "date": _date_from_url(url), "sitename": None}

    date = doc.date or _date_from_url(url)

    return {
        "text": doc.text,
        "title": doc.title,
        "author": doc.author,
        "date": date,
        "sitename": doc.sitename,
    }


def _date_from_url(url: str) -> str | None:
    m = DATE_IN_URL_RE.search(url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None
