from pathlib import Path

from linkreader.models import ArticleResult, UrlInfo
from linkreader.writer import write_article, _format_article


def _make_result(slug="test-article", date="2021-03-19", text="Article body.", **kwargs):
    info = UrlInfo(
        url=f"https://example.com/news/{slug}",
        site="example.com",
        year=2021,
        section="news",
        slug=slug,
        source_file="test.pdf",
    )
    return ArticleResult(
        url_info=info,
        success=True,
        title=kwargs.get("title", "Test Title"),
        author=kwargs.get("author", "Test Author"),
        date=date,
        text=text,
    )


class TestWriteArticle:
    def test_creates_correct_directory_structure(self, tmp_path):
        result = _make_result()
        path = write_article(result, tmp_path)
        assert path.parent == tmp_path / "example.com" / "2021" / "news"

    def test_filename_includes_date_and_slug(self, tmp_path):
        result = _make_result(slug="my-article", date="2021-03-19")
        path = write_article(result, tmp_path)
        assert path.name == "2021-03-19_my-article.txt"

    def test_filename_without_date(self, tmp_path):
        result = _make_result(slug="my-article", date=None)
        path = write_article(result, tmp_path)
        assert path.name == "my-article.txt"

    def test_collision_appends_counter(self, tmp_path):
        r1 = _make_result(slug="article")
        r2 = _make_result(slug="article")
        r3 = _make_result(slug="article")

        p1 = write_article(r1, tmp_path)
        p2 = write_article(r2, tmp_path)
        p3 = write_article(r3, tmp_path)

        assert p1.name == "2021-03-19_article.txt"
        assert p2.name == "2021-03-19_article_2.txt"
        assert p3.name == "2021-03-19_article_3.txt"

    def test_unknown_year_dir(self, tmp_path):
        info = UrlInfo(
            url="https://example.com/article",
            site="example.com",
            year=None,
            section="news",
            slug="article",
            source_file="test.pdf",
        )
        result = ArticleResult(url_info=info, success=True, text="Body.")
        path = write_article(result, tmp_path)
        assert "unknown_year" in str(path)

    def test_file_content_is_utf8(self, tmp_path):
        result = _make_result(text="Turkce icerik: ozel karakterler")
        path = write_article(result, tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "Turkce icerik" in content


class TestFormatArticle:
    def test_all_fields_present(self):
        result = _make_result(title="Baslik", author="Yazar")
        text = _format_article(result)
        assert "Baslik: Baslik" in text
        assert "Yazar: Yazar" in text
        assert "Tarih: 2021-03-19" in text
        assert "Kaynak: example.com" in text
        assert "URL: https://example.com/news/test-article" in text
        assert "Bolum: news" in text
        assert "Article body." in text

    def test_missing_fields_show_bilinmiyor(self):
        result = _make_result(title=None, author=None, date=None)
        text = _format_article(result)
        assert "Baslik: Bilinmiyor" in text
        assert "Yazar: Bilinmiyor" in text
        assert "Tarih: Bilinmiyor" in text

    def test_separator_line(self):
        result = _make_result()
        text = _format_article(result)
        assert "=" * 60 in text
