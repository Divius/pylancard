import unittest

from mock import patch  # noqa

from pylancard import cli
from pylancard import store
from pylancard import trainer
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


@patch.object(plugins_base.BaseLanguage, 'convert_word',
              side_effect=lambda x: x)
class TestStore(StoreMixin, unittest.TestCase):

    def test_add(self, convert_mock):
        self.store.add_word('word3', 'meaning3')
        self.assertEqual('meaning3', self.store.direct_index['word3'])
        self.assertEqual('word3', self.store.reverse_index['meaning3'])
        convert_mock.assert_any_call('word3')
        convert_mock.assert_any_call('meaning3')

    def test_add_no_overwrite(self, convert_mock):
        self.assertRaises(KeyError, self.store.add_word, 'word1', 'meaning3')
        self.assertEqual('meaning1', self.store.direct_index['word1'])
        self.assertEqual('word1', self.store.reverse_index['meaning1'])
        convert_mock.assert_any_call('word1')
        convert_mock.assert_any_call('meaning3')

    def test_add_overwrite(self, convert_mock):
        self.store.add_word('word1', 'meaning3', may_overwrite=True)
        self.assertEqual('meaning3', self.store.direct_index['word1'])
        self.assertEqual('word1', self.store.reverse_index['meaning3'])
        convert_mock.assert_any_call('word1')
        convert_mock.assert_any_call('meaning3')


class TestTrainer(StoreMixin, unittest.TestCase):

    def test_direct_next(self):
        tr = trainer.Trainer(self.store, trainer.DIRECT)
        for _ in range(10):
            challenge = tr.next()
            self.assertIn(challenge, self.store.direct_index)
            self.assertEqual(challenge, tr.challenge)
            self.assertEqual(self.store.direct_index[challenge], tr.answer)

    def test_reverse_next(self):
        tr = trainer.Trainer(self.store, trainer.REVERSE)
        for _ in range(10):
            challenge = tr.next()
            self.assertIn(challenge, self.store.reverse_index)
            self.assertEqual(challenge, tr.challenge)
            self.assertEqual(self.store.reverse_index[challenge], tr.answer)

    @patch.object(plugins_base.BaseLanguage, 'convert_word')
    def test_check(self, convert_mock):
        convert_mock.side_effect = lambda word: word
        tr = trainer.Trainer(self.store, trainer.DIRECT)
        tr.next()
        self.assertTrue(tr.check(tr.answer))
        self.assertFalse(tr.check(tr.answer + 'x'))
        convert_mock.assert_any_call(tr.answer)
        convert_mock.assert_any_call(tr.answer + 'x')


class TestCliAdd(StoreMixin, unittest.TestCase):

    @patch.object(store.Store, 'add_word')
    def test_add_one(self, add_mock):
        cli.add('add', self.store, ['word3=meaning3'])
        add_mock.assert_called_once_with('word3', 'meaning3',
                                         may_overwrite=False)

    @patch.object(store.Store, 'add_word')
    def test_add_one_overwrite(self, add_mock):
        cli.add('add!', self.store, ['word3=meaning3'])
        add_mock.assert_called_once_with('word3', 'meaning3',
                                         may_overwrite=True)