from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import PdfEntry, UrlInfo

YEAR_IN_PATH_RE = re.compile(r"/(2\d{3})/")


def classify(entry: PdfEntry) -> UrlInfo:
    parsed = urlparse(entry.url)
    site = parsed.netloc.removeprefix("www.")
    path_parts = [p for p in parsed.path.strip("/").split("/") if p]

    section = "unknown"
    for part in path_parts:
        if not re.fullmatch(r"\d+", part):
            section = part
            break
    slug = path_parts[-1].split("#")[0] if path_parts else "unknown"
    if len(slug) > 200:
        slug = slug[:200]

    # Year: prefer URL path, fallback to PDF year header
    url_year = _extract_year(parsed.path)
    year = url_year or entry.year

    return UrlInfo(
        url=entry.url,
        site=site,
        year=year,
        section=section,
        slug=slug,
        source_file=entry.source_file,
    )


def _extract_year(path: str) -> int | None:
    m = YEAR_IN_PATH_RE.search(path)
    if m:
        return int(m.group(1))
    return None
