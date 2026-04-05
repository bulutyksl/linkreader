from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .models import ArticleResult

console = Console()


def print_summary(results: list[ArticleResult]) -> None:
    if not results:
        console.print("[yellow]No articles processed.[/yellow]")
        return

    # Group by year
    by_year: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})
    for r in results:
        year_key = str(r.url_info.year or "unknown")
        by_year[year_key]["total"] += 1
        if r.success:
            by_year[year_key]["success"] += 1
        else:
            by_year[year_key]["failed"] += 1

    table = Table(title="Summary")
    table.add_column("Year", style="cyan")
    table.add_column("Total", justify="right")
    table.add_column("Success", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")

    total_all = total_success = total_failed = 0
    for year_key in sorted(by_year):
        d = by_year[year_key]
        table.add_row(year_key, str(d["total"]), str(d["success"]), str(d["failed"]))
        total_all += d["total"]
        total_success += d["success"]
        total_failed += d["failed"]

    table.add_section()
    table.add_row("TOTAL", str(total_all), str(total_success), str(total_failed), style="bold")
    console.print(table)


def write_failed_urls(results: list[ArticleResult], output_dir: Path) -> Path | None:
    failed = [r for r in results if not r.success]
    if not failed:
        return None
    path = output_dir / "failed_urls.txt"
    lines = [f"{r.url_info.url}\t{r.error or 'unknown error'}" for r in failed]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_report_json(results: list[ArticleResult], output_dir: Path) -> Path:
    path = output_dir / "report.json"
    data = []
    for r in results:
        data.append({
            "url": r.url_info.url,
            "site": r.url_info.site,
            "year": r.url_info.year,
            "section": r.url_info.section,
            "success": r.success,
            "title": r.title,
            "date": r.date,
            "error": r.error,
            "output_path": r.output_path,
        })
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
