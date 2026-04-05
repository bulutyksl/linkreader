from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table

from .extractor import extract_article
from .fetcher import FetchError, Fetcher
from .models import ArticleResult
from .pdf_parser import parse_input
from .reporter import console as report_console
from .reporter import print_summary, write_failed_urls, write_report_json
from .url_classifier import classify
from .writer import write_article

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="linkreader",
        description="Extract clean article text from news URLs in PDF/TXT files.",
    )
    parser.add_argument("files", nargs="+", help="PDF or TXT files containing news URLs")
    parser.add_argument("--output", "-o", default="./output", help="Output directory (default: ./output)")
    parser.add_argument("--delay", "-d", type=float, default=2.0, help="Seconds between requests (default: 2.0)")
    parser.add_argument("--retry", "-r", type=int, default=3, help="Max retry attempts per URL (default: 3)")
    parser.add_argument("--resume", action="store_true", help="Skip URLs that already have output files")
    parser.add_argument("--dry-run", action="store_true", help="Parse input files and show URL counts without fetching")
    args = parser.parse_args()

    output_dir = Path(args.output)

    # Parse all input files
    all_entries = []
    for filepath in args.files:
        p = Path(filepath)
        if not p.exists():
            console.print(f"[red]File not found: {filepath}[/red]")
            continue
        entries = parse_input(p)
        all_entries.extend(entries)
        console.print(f"  [green]{p.name}[/green]: {len(entries)} URLs parsed")

    if not all_entries:
        console.print("[red]No URLs found in input files.[/red]")
        sys.exit(1)

    # Classify all URLs
    url_infos = [classify(e) for e in all_entries]

    # Dry-run: show summary and exit
    if args.dry_run:
        _print_dry_run(url_infos)
        return

    # Full run: fetch, extract, write
    output_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(delay=args.delay, max_retries=args.retry)
    results: list[ArticleResult] = []

    # Group by site for organized progress
    by_site: dict[str, list] = defaultdict(list)
    for info in url_infos:
        by_site[info.site].append(info)

    try:
        for site, infos in by_site.items():
            console.print(f"\n[bold]Fetching articles from {site}[/bold] ({len(infos)} URLs)")

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(site, total=len(infos))

                for info in infos:
                    # Resume: check if output file already exists
                    if args.resume:
                        expected_dir = output_dir / info.site / str(info.year or "unknown_year") / info.section
                        if expected_dir.exists() and any(expected_dir.glob(f"*{info.slug}*")):
                            results.append(ArticleResult(
                                url_info=info, success=True,
                                error="skipped (resume)",
                                output_path=str(expected_dir),
                            ))
                            progress.advance(task)
                            continue

                    result = _process_url(fetcher, info, output_dir)
                    results.append(result)
                    progress.advance(task)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted! Writing partial report...[/yellow]")

    # Report
    console.print()
    print_summary(results)
    failed_path = write_failed_urls(results, output_dir)
    report_path = write_report_json(results, output_dir)

    if failed_path:
        console.print(f"\nFailed URLs: [cyan]{failed_path}[/cyan]")
    console.print(f"Full report: [cyan]{report_path}[/cyan]")

    if args.resume:
        console.print("[dim]Tip: re-run with --resume to retry failed URLs[/dim]")


def _process_url(fetcher: Fetcher, info, output_dir: Path) -> ArticleResult:
    try:
        html = fetcher.fetch(info.url)
    except FetchError as e:
        return ArticleResult(url_info=info, success=False, error=str(e))
    except Exception as e:
        return ArticleResult(url_info=info, success=False, error=f"fetch error: {e}")

    try:
        article_data = extract_article(html, info.url)
    except Exception as e:
        return ArticleResult(url_info=info, success=False, error=f"extraction error: {e}")

    if not article_data.get("text"):
        return ArticleResult(url_info=info, success=False, error="no content extracted")

    result = ArticleResult(
        url_info=info,
        success=True,
        title=article_data.get("title"),
        author=article_data.get("author"),
        date=article_data.get("date"),
        text=article_data.get("text"),
    )

    try:
        path = write_article(result, output_dir)
        result.output_path = str(path)
    except Exception as e:
        result.success = False
        result.error = f"write error: {e}"

    return result


def _print_dry_run(url_infos) -> None:
    console.print(f"\n[bold]Total URLs: {len(url_infos)}[/bold]\n")

    # Group by year
    by_year: dict[str, list] = defaultdict(list)
    for info in url_infos:
        by_year[str(info.year or "unknown")].append(info)

    table = Table(title="URLs by Year")
    table.add_column("Year", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Sections", style="dim")

    for year_key in sorted(by_year):
        infos = by_year[year_key]
        sections = sorted(set(i.section for i in infos))
        table.add_row(year_key, str(len(infos)), ", ".join(sections))

    console.print(table)

    # Group by site
    sites = sorted(set(i.site for i in url_infos))
    if len(sites) > 1:
        console.print(f"\nSites: {', '.join(sites)}")
