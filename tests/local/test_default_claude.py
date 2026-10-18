"""Direct ask_ai calls select Claude; no network or real student persistence."""
import copy
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import ai_test
from claude_provider import ClaudeError
from learning_result import LearningResult
from local_store import BufferedConversation


class DefaultClaudeTests(unittest.TestCase):
    def setUp(self):
        self.storage = BufferedConversation({'profile': {'grade': 10, 'country': 'US'},
            'history': [], 'attempts': []})
        self.provider = SimpleNamespace(responses=SimpleNamespace(parse=Mock(return_value=
            SimpleNamespace(output_parsed=LearningResult(reply='Synthetic reply', is_attempt=False), status='completed'))))
        self.settings = {'NMI_ENABLE_AI': '1', 'NMI_ENABLE_ANTHROPIC_PAID': '1',
                         'NMI_CLAUDE_MODEL': 'claude-synthetic-model'}
        self.network = patch.object(socket.socket, 'connect', side_effect=AssertionError('No network'))
        self.network.start(); self.addCleanup(self.network.stop)
        self.global_client = patch.object(ai_test, 'client', None)
        self.global_client.start(); self.addCleanup(self.global_client.stop)

    def ask(self, **options):
        return ai_test.ask_ai('Synthetic learner', '10', 'Testland', 'ar', 'اشرح بمثال أبسط',
                              storage=self.storage, **options)

    def test_direct_call_selects_claude_with_configured_model(self):
        with patch.dict('os.environ', self.settings, clear=True), patch('claude_provider.ClaudeProvider', return_value=self.provider) as factory:
            self.assertEqual(self.ask(), 'Synthetic reply')
        factory.assert_called_once_with('claude-synthetic-model')
        self.assertEqual(self.provider.responses.parse.call_args.kwargs['model'], 'claude-synthetic-model')
        self.assertEqual(len(self.storage.state['history']), 2)
        self.assertEqual(self.storage.state['attempts'], [])

    def test_both_gates_required_before_storage_or_provider_use(self):
        for settings in ({}, {'NMI_ENABLE_AI':'1'}, {'NMI_ENABLE_ANTHROPIC_PAID':'1'}):
            with self.subTest(settings=settings), patch.dict('os.environ', settings, clear=True), patch('claude_provider.ClaudeProvider') as factory:
                with self.assertRaises(ClaudeError) as error: self.ask()
                self.assertEqual(error.exception.code, 'claude_locked')
                factory.assert_not_called()
        self.assertEqual(self.storage.state['history'], [])

    def test_model_required_without_openai_fallback(self):
        with patch.dict('os.environ', self.settings | {'NMI_CLAUDE_MODEL':''}, clear=True):
            with self.assertRaises(ClaudeError) as error: self.ask()
        self.assertEqual(error.exception.code, 'claude_model')
        self.assertEqual(self.storage.state['history'], [])

    def test_injected_web_provider_and_model_preserved(self):
        with patch.dict('os.environ', {}, clear=True), patch('claude_provider.ClaudeProvider') as factory:
            self.assertEqual(self.ask(ai_client=self.provider, model='synthetic-explicit-model', web_policy=True), 'Synthetic reply')
            factory.assert_not_called()
        self.assertEqual(self.provider.responses.parse.call_args.kwargs['model'], 'synthetic-explicit-model')

    def test_failure_preserves_prior_conversation(self):
        self.storage.state['history'] = [{'role':'assistant','content':'Earlier synthetic reply'}]
        before = copy.deepcopy(self.storage.state)
        self.provider.responses.parse.side_effect = ClaudeError('claude_key')
        with patch.dict('os.environ', self.settings, clear=True), patch('claude_provider.ClaudeProvider', return_value=self.provider):
            with self.assertRaises(ClaudeError): self.ask()
        self.assertEqual(self.storage.state, before)


if __name__ == '__main__': unittest.main()
