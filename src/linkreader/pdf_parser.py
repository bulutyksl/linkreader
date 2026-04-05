from __future__ import annotations

import re
from pathlib import Path

import fitz

from .models import PdfEntry

YEAR_HEADER_RE = re.compile(r"(2\d{3})\s*[-\u2013]\s*(?:\d+\s+haber|haber yok)")
URL_RE = re.compile(r"https?://\S+")


def parse_pdf(path: str | Path) -> list[PdfEntry]:
    path = Path(path)
    doc = fitz.open(str(path))
    entries = _extract_via_links(doc, path.name)
    if not entries:
        entries = _extract_via_text(doc, path.name)
    doc.close()
    # Deduplicate by URL, preserving order
    seen: set[str] = set()
    unique: list[PdfEntry] = []
    for e in entries:
        if e.url not in seen:
            seen.add(e.url)
            unique.append(e)
    return unique


def parse_txt(path: str | Path) -> list[PdfEntry]:
    path = Path(path)
    entries: list[PdfEntry] = []
    current_year: int | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            # Check if comment contains a year hint like "# 2021"
            m = re.search(r"(2\d{3})", line)
            if m:
                current_year = int(m.group(1))
            continue
        if URL_RE.match(line):
            entries.append(PdfEntry(url=line, year=current_year, source_file=path.name))
    return entries


def parse_input(path: str | Path) -> list[PdfEntry]:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return parse_pdf(path)
    return parse_txt(path)


def _extract_via_links(doc: fitz.Document, source_name: str) -> list[PdfEntry]:
    entries: list[PdfEntry] = []
    current_year: int | None = None

    for page in doc:
        # Find year headers and their y-positions on this page
        year_positions = _find_year_headers(page)

        for link in page.get_links():
            if link.get("kind") != fitz.LINK_URI:
                continue
            url = link.get("uri", "")
            if not url.startswith("http"):
                continue

            link_y = link["from"].y0

            # Find the nearest preceding year header
            applicable = [(y, yr) for y, yr in year_positions if y < link_y]
            if applicable:
                current_year = max(applicable, key=lambda x: x[0])[1]

            entries.append(PdfEntry(url=url, year=current_year, source_file=source_name))

    return entries


def _extract_via_text(doc: fitz.Document, source_name: str) -> list[PdfEntry]:
    entries: list[PdfEntry] = []
    current_year: int | None = None
    partial_url = ""

    for page in doc:
        text = page.get_text()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            m = YEAR_HEADER_RE.search(line)
            if m:
                current_year = int(m.group(1))
                continue

            # Handle line-wrapped URLs
            if partial_url:
                if not line.startswith("http"):
                    partial_url += line
                    continue
                else:
                    entries.append(
                        PdfEntry(url=partial_url, year=current_year, source_file=source_name)
                    )
                    partial_url = ""

            url_match = URL_RE.search(line)
            if url_match:
                url = url_match.group(0)
                # Check if URL might continue on next line (heuristic: line is long)
                if len(line) > 80 and not line.endswith(("/", ")")):
                    partial_url = url
                else:
                    entries.append(PdfEntry(url=url, year=current_year, source_file=source_name))

    if partial_url:
        entries.append(PdfEntry(url=partial_url, year=current_year, source_file=source_name))

    return entries


def _find_year_headers(page: fitz.Page) -> list[tuple[float, int]]:
    year_positions: list[tuple[float, int]] = []
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            text = "".join(span["text"] for span in line["spans"])
            m = YEAR_HEADER_RE.search(text)
            if m:
                y_pos = line["bbox"][1]
                year_positions.append((y_pos, int(m.group(1))))
    return year_positions
