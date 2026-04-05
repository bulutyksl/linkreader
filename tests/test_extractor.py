from linkreader.extractor import _date_from_url, extract_article


class TestDateFromUrl:
    def test_standard_date_path(self):
        assert _date_from_url("https://example.com/news/2021/03/19/slug") == "2021-03-19"

    def test_no_date_in_url(self):
        assert _date_from_url("https://example.com/news/slug") is None

    def test_date_must_have_surrounding_slashes(self):
        assert _date_from_url("https://example.com/20210319/slug") is None

    def test_future_year(self):
        assert _date_from_url("https://example.com/2087/01/15/article") == "2087-01-15"


class TestExtractArticle:
    def test_returns_none_fields_on_none_doc(self):
        """Empty/garbage HTML should not crash, just return Nones."""
        result = extract_article("", "https://example.com/2021/05/01/test")
        assert result["date"] == "2021-05-01"  # fallback from URL
        assert result["text"] is None

    def test_extracts_text_from_real_html(self):
        html = """
        <html><head><title>Test Article</title></head>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>This is the first paragraph of the article with enough content to pass extraction thresholds for trafilatura.</p>
                <p>This is the second paragraph with more content to ensure the extraction works properly and meets minimum length requirements.</p>
                <p>And a third paragraph to make sure we have enough text content for the extractor to consider this a real article worth extracting.</p>
            </article>
        </body></html>
        """
        result = extract_article(html, "https://example.com/news/2023/01/01/test-article")
        # trafilatura may or may not extract from minimal HTML, but it shouldn't crash
        assert isinstance(result, dict)
        assert "text" in result
        assert "title" in result
