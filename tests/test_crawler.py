from src.crawler import PoliteCrawler


HOME_HTML = """
<html><body>
  <a href="/page/2/">Next</a>
  <a href="https://external.example/ignore/">External</a>
  <a href="#fragment">Fragment</a>
</body></html>
"""
PAGE_2_HTML = "<html><body><p>Last page</p></body></html>"


def test_extract_links_keeps_only_same_site_links():
    crawler = PoliteCrawler("https://quotes.toscrape.com/", delay_seconds=0)
    links = crawler.extract_links(HOME_HTML, "https://quotes.toscrape.com/")
    assert "https://quotes.toscrape.com/page/2/" in links
    assert "https://external.example/ignore/" not in links


def test_crawl_uses_breadth_first_traversal_without_network(monkeypatch):
    crawler = PoliteCrawler("https://quotes.toscrape.com/", delay_seconds=0, max_pages=10)

    pages = {
        "https://quotes.toscrape.com/": HOME_HTML,
        "https://quotes.toscrape.com/page/2/": PAGE_2_HTML,
    }

    def fake_request(url):
        return pages[url]

    monkeypatch.setattr(crawler, "_request", fake_request)
    crawled = crawler.crawl()

    assert [page.url for page in crawled] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
