import json

from linkreader.models import ArticleResult, UrlInfo
from linkreader.reporter import write_failed_urls, write_report_json


def _info(year=2021):
    return UrlInfo(
        url="https://example.com/article",
        site="example.com",
        year=year,
        section="news",
        slug="article",
        source_file="test.pdf",
    )


class TestWriteFailedUrls:
    def test_no_failures_returns_none(self, tmp_path):
        results = [ArticleResult(url_info=_info(), success=True)]
        assert write_failed_urls(results, tmp_path) is None

    def test_writes_failed_urls_with_errors(self, tmp_path):
        results = [
            ArticleResult(url_info=_info(), success=False, error="timeout"),
            ArticleResult(url_info=_info(), success=True),
            ArticleResult(url_info=_info(), success=False, error="404"),
        ]
        path = write_failed_urls(results, tmp_path)
        assert path is not None
        content = path.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 2
        assert "timeout" in lines[0]
        assert "404" in lines[1]

    def test_none_error_shows_unknown(self, tmp_path):
        results = [ArticleResult(url_info=_info(), success=False, error=None)]
        path = write_failed_urls(results, tmp_path)
        content = path.read_text()
        assert "unknown error" in content


class TestWriteReportJson:
    def test_writes_valid_json(self, tmp_path):
        results = [
            ArticleResult(url_info=_info(), success=True, title="Test"),
            ArticleResult(url_info=_info(), success=False, error="fail"),
        ]
        path = write_report_json(results, tmp_path)
        data = json.loads(path.read_text())
        assert len(data) == 2
        assert data[0]["success"] is True
        assert data[0]["title"] == "Test"
        assert data[1]["success"] is False
        assert data[1]["error"] == "fail"

    def test_handles_none_fields(self, tmp_path):
        results = [ArticleResult(url_info=_info(), success=True)]
        path = write_report_json(results, tmp_path)
        data = json.loads(path.read_text())
        assert data[0]["title"] is None
        assert data[0]["date"] is None
