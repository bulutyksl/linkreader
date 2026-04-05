from linkreader.models import PdfEntry
from linkreader.url_classifier import classify, _extract_year


def _entry(url, year=None):
    return PdfEntry(url=url, year=year, source_file="test.pdf")


class TestClassify:
    def test_takvim_style_url(self):
        """takvim.com.tr: /section/year/month/day/slug"""
        info = classify(_entry("https://www.takvim.com.tr/guncel/2021/03/19/istanbul-sozlesmesi"))
        assert info.site == "takvim.com.tr"
        assert info.section == "guncel"
        assert info.year == 2021
        assert info.slug == "istanbul-sozlesmesi"

    def test_year_first_url_skips_numeric_sections(self):
        """Sites like example.com/2021/03/19/slug should not have section='2021'"""
        info = classify(_entry("https://example.com/2021/03/19/some-article"))
        assert info.section == "some-article"
        assert info.year == 2021

    def test_all_numeric_path_gives_unknown_section(self):
        """Path like /2021/03/19/ with no non-numeric segment"""
        info = classify(_entry("https://example.com/2021/03/19/"))
        assert info.section == "unknown"

    def test_www_prefix_stripped(self):
        info = classify(_entry("https://www.example.com/news/article"))
        assert info.site == "example.com"

    def test_slug_truncated_at_200(self):
        long_slug = "a" * 300
        info = classify(_entry(f"https://example.com/news/{long_slug}"))
        assert len(info.slug) == 200

    def test_slug_fragment_stripped(self):
        info = classify(_entry("https://example.com/news/article#comments"))
        assert info.slug == "article"

    def test_year_from_url_takes_precedence_over_pdf_year(self):
        info = classify(_entry("https://example.com/news/2023/05/01/article", year=2020))
        assert info.year == 2023

    def test_falls_back_to_pdf_year_when_no_year_in_url(self):
        info = classify(_entry("https://example.com/news/article", year=2020))
        assert info.year == 2020

    def test_no_year_anywhere(self):
        info = classify(_entry("https://example.com/news/article"))
        assert info.year is None

    def test_bare_domain_no_path(self):
        info = classify(_entry("https://example.com"))
        assert info.section == "unknown"
        assert info.slug == "unknown"


class TestExtractYear:
    def test_year_in_path(self):
        assert _extract_year("/guncel/2021/03/19/slug") == 2021

    def test_no_year(self):
        assert _extract_year("/news/article") is None

    def test_future_year(self):
        assert _extract_year("/news/2087/01/01/article") == 2087
