from unittest import TestCase

from check_narrative_schema_hml import numeric_fragments


class NarrativeProbeTests(TestCase):
    def test_fragments_locate_numbers_and_redact_credentials(self):
        draft = {'current_commentary': 'Boletim sobre COVID-19. gsk_secret123 e sk-proj-secret456.',
                 'historical_commentary': 'Chave confidencial789 e nenhum dado individual.',
                 'reasoning': 'Não deve ser exibido: 12345'}
        fragments = numeric_fragments(draft, 'confidencial789')
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0]['field'], 'current_commentary')
        self.assertIn('COVID-19', fragments[0]['fragment'])
        self.assertNotIn('gsk_secret123', str(fragments))
        self.assertNotIn('sk-proj-secret456', str(fragments))
        self.assertNotIn('confidencial789', str(fragments))
        self.assertNotIn('12345', str(fragments))

    def test_fragments_are_bounded_and_ignore_non_text(self):
        fragments = numeric_fragments({'current_commentary': ' '.join(str(i) for i in range(100)),
                                       'historical_commentary': None}, '')
        self.assertEqual(len(fragments), 5)
        self.assertTrue(all(len(item['fragment']) <= 51 for item in fragments))
        self.assertEqual(numeric_fragments([], ''), [])
