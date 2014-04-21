import unittest

from mock import patch  # noqa

from pylancard import commands
from pylancard import store
from pylancard.plugins import base as plugins_base


class FakeStore(store.Store):

    def __init__(self):
        self.languages = ('1', '2')
        self.direct_index = {
            'word1': 'meaning1',
            'word2': 'meaning2',
        }
        self.reverse_index = {
            'meaning1': 'word1',
            'meaning2': 'word2',
        }
        self.original_plugin = plugins_base.BaseLanguage(self)
        self.meaning_plugin = plugins_base.BaseLanguage(self)


class StoreMixin:

    def setUp(self):
        super().setUp()
        self.store = FakeStore()


@patch.object(plugins_base.BaseLanguage, 'convert_word')
class TestCommandsAdd(StoreMixin, unittest.TestCase):

    def test_add_one(self, lang_mock):
        lang_mock.side_effect = lambda word: word
        commands.add('add', self.store, ['word3=meaning3'])
        self.assertEqual('meaning3', self.store.direct_index['word3'])
        self.assertEqual('word3', self.store.reverse_index['meaning3'])
        lang_mock.assert_any_call('word3')
        lang_mock.assert_any_call('meaning3')
