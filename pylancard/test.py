import builtins
import os
import tempfile
import unittest

from mock import patch, sentinel  # noqa

from pylancard import cli
from pylancard import store
from pylancard import trainer
from pylancard.plugins import base as plugins_base
from pylancard.plugins import cz as lang_cz


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
        self.store.add('word3', 'meaning3')
        self.assertEqual('meaning3', self.store.direct_index['word3'])
        self.assertEqual('word3', self.store.reverse_index['meaning3'])
        convert_mock.assert_any_call('word3')
        convert_mock.assert_any_call('meaning3')

    def test_add_no_overwrite(self, convert_mock):
        self.assertRaises(KeyError, self.store.add, 'word1', 'meaning3')
        self.assertEqual('meaning1', self.store.direct_index['word1'])
        self.assertEqual('word1', self.store.reverse_index['meaning1'])
        convert_mock.assert_any_call('word1')
        convert_mock.assert_any_call('meaning3')

    def test_add_overwrite(self, convert_mock):
        self.store.add('word1', 'meaning3', may_overwrite=True)
        self.assertEqual('meaning3', self.store.direct_index['word1'])
        self.assertEqual('word1', self.store.reverse_index['meaning3'])
        convert_mock.assert_any_call('word1')
        convert_mock.assert_any_call('meaning3')


class TestStoreIO(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.dir = tempfile.mkdtemp()

    def test_create_open(self):
        filename = os.path.join(self.dir, 'file')
        store.create(filename, ('cz', 'Oo'))
        new_store = store.Store(filename)
        self.assertEqual(('cz', 'Oo'), new_store.languages)
        self.assertEqual({}, new_store.direct_index)
        self.assertEqual({}, new_store.reverse_index)
        self.assertIsInstance(new_store.original_plugin, lang_cz.Czech)
        self.assertIsInstance(new_store.meaning_plugin,
                              plugins_base.BaseLanguage)

    def test_create_open_save(self):
        filename = os.path.join(self.dir, 'file')
        store.create(filename, ('cz', 'Oo'))
        with store.Store(filename) as new_store:
            new_store.direct_index['word'] = 'meaning'
        new_store = store.Store(filename)
        self.assertEqual({'word': 'meaning'}, new_store.direct_index)
        self.assertEqual({'meaning': 'word'}, new_store.reverse_index)


class TestTrainer(StoreMixin, unittest.TestCase):

    def test_unexpected_kind(self):
        self.assertRaises(ValueError, trainer.Trainer, self.store, "42")

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


class TestBaseLanguage(unittest.TestCase):

    def test_convert_word(self):
        class Test(plugins_base.BaseLanguage):
            patterns = {'bb': 'BB'}

        self.assertEqual('aBBccBB', Test(None).convert_word('abbccbb'))

    def test_present(self):
        self.assertFalse(plugins_base.BaseLanguage(None).present)
        desc = type('Test', (plugins_base.BaseLanguage,), {})
        self.assertTrue(desc.present)


@patch.object(store.Store, 'add')
class TestCliAdd(StoreMixin, unittest.TestCase):

    def test_add_one(self, add_mock):
        cli.add('add', self.store, ['word3=meaning3'])
        add_mock.assert_called_once_with('word3', 'meaning3',
                                         may_overwrite=False)

    def test_add_one_overwrite(self, add_mock):
        cli.add('add!', self.store, ['word3=meaning3'])
        add_mock.assert_called_once_with('word3', 'meaning3',
                                         may_overwrite=True)


@patch.object(builtins, 'print')
class TestCliList(StoreMixin, unittest.TestCase):

    def test_list(self, print_mock):
        cli.list_('list', self.store, [])
        print_mock.assert_any_call("word1\tmeaning1")
        print_mock.assert_any_call("word2\tmeaning2")
        self.assertEqual(2, print_mock.call_count)


@patch.object(builtins, 'input')
@patch.object(builtins, 'print')
@patch.object(trainer, 'Trainer')
class TestCliTrainer(unittest.TestCase):

    def test_train(self, trainer_mock, print_mock, input_mock):
        trainer_mock.return_value.next.return_value = 'word'
        input_mock.side_effect = EOFError()
        cli.train('cmd', sentinel.store, [])
        trainer_mock.return_value.next.assert_called_once_with()
        print_mock.assert_any_call("Next word: word")

    def test_correct(self, trainer_mock, print_mock, input_mock):
        trainer_mock.return_value.next.side_effect = ['word1', 'word2']
        trainer_mock.return_value.check.return_value = True
        input_mock.side_effect = ['word1', EOFError()]
        cli.train('cmd', sentinel.store, [])
        trainer_mock.return_value.next.assert_called_with()
        self.assertEqual(2, trainer_mock.return_value.next.call_count)
        print_mock.assert_any_call("Next word: word1")
        print_mock.assert_any_call("Next word: word2")

    def test_incorrect(self, trainer_mock, print_mock, input_mock):
        trainer_mock.return_value.next.return_value = 'word'
        trainer_mock.return_value.check.return_value = False
        input_mock.side_effect = ['word1', EOFError()]
        cli.train('cmd', sentinel.store, [])
        trainer_mock.return_value.next.assert_called_once_with()
        print_mock.assert_any_call("Next word: word")
        print_mock.assert_any_call("Wrong, try again")

    def test_skip(self, trainer_mock, print_mock, input_mock):
        trainer_mock.return_value.next.side_effect = ['word1', 'word2']
        input_mock.side_effect = ['/skip', EOFError()]
        cli.train('cmd', sentinel.store, [])
        trainer_mock.return_value.next.assert_called_with()
        self.assertEqual(2, trainer_mock.return_value.next.call_count)
        self.assertFalse(trainer_mock.return_value.check.called)
        print_mock.assert_any_call("Next word: word1")
        print_mock.assert_any_call("Next word: word2")

    def test_quit(self, trainer_mock, print_mock, input_mock):
        trainer_mock.return_value.next.return_value = 'word'
        input_mock.return_value = '/quit'
        cli.train('cmd', sentinel.store, [])
        trainer_mock.return_value.next.assert_called_once_with()
        self.assertFalse(trainer_mock.return_value.check.called)
