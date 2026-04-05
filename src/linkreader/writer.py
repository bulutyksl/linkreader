from __future__ import annotations

from pathlib import Path

from .models import ArticleResult


def write_article(article: ArticleResult, output_dir: Path) -> Path:
    info = article.url_info
    year_str = str(info.year) if info.year else "unknown_year"
    dir_path = output_dir / info.site / year_str / info.section
    dir_path.mkdir(parents=True, exist_ok=True)

    # Build filename: YYYY-MM-DD_slug.txt
    date_prefix = article.date or ""
    if date_prefix:
        filename = f"{date_prefix}_{info.slug}.txt"
    else:
        filename = f"{info.slug}.txt"

    filepath = dir_path / filename

    # Handle collisions
    if filepath.exists():
        counter = 2
        while True:
            stem = filepath.stem
            candidate = dir_path / f"{stem}_{counter}.txt"
            if not candidate.exists():
                filepath = candidate
                break
            counter += 1

    filepath.write_text(
        _format_article(article),
        encoding="utf-8",
    )
    return filepath


def _format_article(article: ArticleResult) -> str:
    info = article.url_info
    lines = [
        f"Baslik: {article.title or 'Bilinmiyor'}",
        f"Tarih: {article.date or 'Bilinmiyor'}",
        f"Yazar: {article.author or 'Bilinmiyor'}",
        f"Kaynak: {info.site}",
        f"URL: {info.url}",
        f"Bolum: {info.section}",
        "=" * 60,
        "",
        article.text or "",
    ]
    return "\n".join(lines)
