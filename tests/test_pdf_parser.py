import textwrap
from pathlib import Path

from linkreader.pdf_parser import parse_txt


class TestParseTxt:
    def test_basic_urls(self, tmp_path):
        f = tmp_path / "urls.txt"
        f.write_text(
            "https://example.com/article1\n"
            "https://example.com/article2\n"
        )
        entries = parse_txt(f)
        assert len(entries) == 2
        assert entries[0].url == "https://example.com/article1"
        assert entries[1].url == "https://example.com/article2"

    def test_year_from_comment(self, tmp_path):
        f = tmp_path / "urls.txt"
        f.write_text(textwrap.dedent("""\
            # 2021
            https://example.com/article1
            https://example.com/article2
            # 2022
            https://example.com/article3
        """))
        entries = parse_txt(f)
        assert entries[0].year == 2021
        assert entries[1].year == 2021
        assert entries[2].year == 2022

    def test_blank_lines_and_comments_skipped(self, tmp_path):
        f = tmp_path / "urls.txt"
        f.write_text(textwrap.dedent("""\
            # This is a comment without a year
            https://example.com/article1

            # Another comment
            https://example.com/article2
        """))
        entries = parse_txt(f)
        assert len(entries) == 2

    def test_no_year_gives_none(self, tmp_path):
        f = tmp_path / "urls.txt"
        f.write_text("https://example.com/article\n")
        entries = parse_txt(f)
        assert entries[0].year is None

    def test_non_url_lines_ignored(self, tmp_path):
        f = tmp_path / "urls.txt"
        f.write_text(
            "this is not a url\n"
            "https://example.com/real\n"
            "also not a url\n"
        )
        entries = parse_txt(f)
        assert len(entries) == 1
        assert entries[0].url == "https://example.com/real"

    def test_source_file_set(self, tmp_path):
        f = tmp_path / "my-urls.txt"
        f.write_text("https://example.com/article\n")
        entries = parse_txt(f)
        assert entries[0].source_file == "my-urls.txt"

    def test_future_year_in_comment(self, tmp_path):
        f = tmp_path / "urls.txt"
        f.write_text("# 2087\nhttps://example.com/future\n")
        entries = parse_txt(f)
        assert entries[0].year == 2087
