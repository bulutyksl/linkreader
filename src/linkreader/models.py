from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PdfEntry:
    url: str
    year: int | None
    source_file: str


@dataclass
class UrlInfo:
    url: str
    site: str
    year: int | None
    section: str
    slug: str
    source_file: str


@dataclass
class ArticleResult:
    url_info: UrlInfo
    success: bool
    title: str | None = None
    author: str | None = None
    date: str | None = None
    text: str | None = None
    error: str | None = None
    output_path: str | None = None
