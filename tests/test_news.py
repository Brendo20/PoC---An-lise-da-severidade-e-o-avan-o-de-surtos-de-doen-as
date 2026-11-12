from datetime import datetime, timezone
from io import BytesIO
from unittest import TestCase

from srag.news import FeedRedirect, NewsSearch, parse_feed, safe_url

NOW = datetime(2026, 11, 12, tzinfo=timezone.utc)
RSS = b'''<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<item><title>SRAG: boletim</title><link>https://example.org/srag</link><description>&lt;b&gt;Resumo&lt;/b&gt;</description><dc:date>2026-11-11T12:00:00Z</dc:date></item></rdf:RDF>'''


class NewsTests(TestCase):
    def test_rdf_namespaces_and_html_cleaning(self):
        articles = parse_feed(RSS, 'Fixture', NOW)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['excerpt'], 'Resumo')
        self.assertEqual(articles[0]['source'], 'Fixture')

    def test_atom_and_dates_topic_url_filters(self):
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>InfoGripe</title><link href="https://example.org/srag"/><updated>2026-11-11T12:00:00Z</updated></entry></feed>'
        self.assertEqual(len(parse_feed(atom, 'Fixture', NOW)), 1)
        for raw in [RSS.replace(b'2026-11-11', b'2019-11-11'), RSS.replace(b'2026-11-11', b'2026-11-30'),
                    RSS.replace(b'https://example.org/srag', b'javascript:alert(1)'),
                    RSS.replace(b'SRAG: boletim', b'Outra noticia')]:
            self.assertEqual(parse_feed(raw, 'Fixture', NOW), [])

    def test_entity_size_and_unsafe_links(self):
        for raw in (b'<!DOCTYPE x><rss/>', b'x' * 1500001):
            with self.assertRaises(ValueError):
                parse_feed(raw, 'Fixture', NOW)
        for url in ('http://example.org', 'https://user:secret@example.org', 'https://example.org:22', 'javascript:alert(1)'):
            self.assertFalse(safe_url(url))
        with self.assertRaises(ValueError):
            FeedRedirect().redirect_request(None, None, 302, '', {}, 'https://internal.invalid')

    def test_deduplication_and_partial_sources(self):
        requests = []
        def opener(request, timeout):
            requests.append(request.full_url)
            return BytesIO(RSS)
        result = NewsSearch(opener, lambda: NOW).search()
        self.assertEqual(result['status'], 'available')
        self.assertEqual(len(result['articles']), 1)
        self.assertEqual(len(requests), 3)
        def failed(*args, **kwargs):
            raise OSError('private network detail')
        result = NewsSearch(failed, lambda: NOW).search()
        self.assertEqual(result['status'], 'unavailable')
        self.assertNotIn('private network detail', str(result))
