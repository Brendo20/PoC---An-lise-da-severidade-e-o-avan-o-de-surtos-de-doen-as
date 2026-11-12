import json
import urllib.error
from io import BytesIO
from unittest import TestCase

from srag.groq_client import GroqClient, NoRedirect, ProviderError


class GroqTests(TestCase):
    def test_headers_structured_output_and_reasoning_not_retained(self):
        captured = []
        def opener(request, timeout):
            captured.append(request)
            return BytesIO(json.dumps({'id': 'test', 'choices': [{'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': '{}', 'reasoning': 'private reasoning'}}],
                'usage': {'total_tokens': 12}}).encode())
        result = GroqClient('fixture-key', opener=opener).complete([], schema={'type': 'object'})
        self.assertNotIn('reasoning', str(result))
        self.assertEqual(result['usage']['total_tokens'], 12)
        request = captured[0]
        self.assertEqual(request.get_header('User-agent'), 'indicium-srag-poc/0.1')
        self.assertEqual(request.get_header('Authorization'), 'Bearer fixture-key')
        self.assertTrue(json.loads(request.data)['response_format']['json_schema']['strict'])
        self.assertNotIn('tools', json.loads(request.data))
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'https://elsewhere.org'))

    def test_provider_errors_are_sanitized_and_context_is_bounded(self):
        for status, expected in [(401, 'authentication_error'), (403, 'permission_error'), (429, 'rate_limit')]:
            def opener(*args, **kwargs):
                raise urllib.error.HTTPError('https://api.groq.com', status, 'secret-key', {}, BytesIO(b'secret'))
            with self.assertRaises(ProviderError) as error:
                GroqClient('fixture', opener=opener).complete([])
            self.assertEqual(str(error.exception), expected)
        with self.assertRaises(ProviderError) as error:
            GroqClient('fixture').complete([{'content': 'x' * 28001}])
        self.assertEqual(str(error.exception), 'context_limit')

    def test_unconfigured_oversized_and_invalid_responses(self):
        with self.assertRaises(ProviderError):
            GroqClient('').complete([])
        for raw in (b'invalid', b'x' * 1048577, b'{"choices":[]}'):
            with self.assertRaises(ProviderError):
                GroqClient('fixture', opener=lambda *args, **kwargs: BytesIO(raw)).complete([])

    def test_gpt_oss_tool_requests_explicitly_disable_parallel_calls(self):
        captured = []
        def opener(request, timeout):
            captured.append(json.loads(request.data))
            return BytesIO(json.dumps({'choices': [{'finish_reason': 'tool_calls', 'message': {
                'tool_calls': [{'id': 'fixture', 'function': {'name': 'consultar_metricas', 'arguments': '{}'}}]}}]}).encode())
        GroqClient('fixture', opener=opener).complete([], tools=[{'type': 'function', 'function': {
            'name': 'consultar_metricas', 'parameters': {'type': 'object', 'properties': {}}}}])
        self.assertIs(captured[0]['parallel_tool_calls'], False)
        self.assertEqual(captured[0]['max_completion_tokens'], 512)
        self.assertEqual(captured[0]['tool_choice'], {'type': 'function', 'function': {'name': 'consultar_metricas'}})

    def test_tool_configuration_refuses_ambiguous_multi_tool_request(self):
        tools = [{'function': {'name': 'a'}}, {'function': {'name': 'b'}}]
        with self.assertRaises(ProviderError) as error:
            GroqClient('fixture').complete([], tools=tools)
        self.assertEqual(error.exception.code, 'invalid_tool_configuration')

    def test_http_diagnostic_retains_status_and_allowlisted_code_only(self):
        raw = json.dumps({'error': {'code': 'tool_use_failed', 'message': 'fixture-secret',
                                   'failed_generation': 'private reasoning'}}).encode()
        def opener(*args, **kwargs):
            raise urllib.error.HTTPError('https://api.groq.com', 400, '', {}, BytesIO(raw))
        with self.assertRaises(ProviderError) as error:
            GroqClient('fixture-secret', opener=opener).complete([])
        self.assertEqual(error.exception.code, 'provider_http_400')
        self.assertEqual(error.exception.diagnostic(), {'http_status': 400, 'provider_code': 'tool_use_failed', 'retry_after_seconds': None})
        self.assertNotIn('fixture-secret', str(error.exception.__dict__))
        self.assertNotIn('private reasoning', str(error.exception.__dict__))

    def test_rate_limit_preserves_only_valid_retry_after_seconds(self):
        for value, expected in [('2.5', 3), ('86401', None), ('nan', None), ('private-value', None)]:
            def opener(*args, **kwargs):
                raise urllib.error.HTTPError('https://api.groq.com', 429, '', {'Retry-After': value}, BytesIO(b'{}'))
            with self.assertRaises(ProviderError) as error:
                GroqClient('fixture', opener=opener).complete([])
            self.assertEqual(error.exception.retry_after_seconds, expected)
