import gzip
import json

from .plugins import base


def create(filename, languages):
    with gzip.open(filename, 'wt') as fp:
        json.dump({'languages': languages,
                   'index': {},
                   'version': 1},
                  fp, indent=2)


class Store(dict):

    _PREFIX = 'pylancard.plugins'

    def __init__(self, filename):
        super().__init__()
        self._filename = filename
        with gzip.open(filename, 'rb') as fp:
            self.update(json.loads(fp.read().decode('utf-8')))

        self.languages = tuple(self['languages'])
        self.direct_index = self['index']
        self.reverse_index = {v: k for (k, v) in self.direct_index.items()}
        self.original_plugin = (self._import_plugin(self.languages[0])
                                or base.BaseLanguage(self))
        self.meaning_plugin = (self._import_plugin(self.languages[1])
                               or base.BaseLanguage(self))

    def save(self):
        self['index'] = self.direct_index
        with gzip.open(self._filename, 'wb') as fp:
            fp.write(json.dumps(self, indent=2).encode('utf-8'))

    close = save

    __enter__ = lambda self: self

    def __exit__(self, *_):
        self.save()

    def add_word(self, word1, word2, may_overwrite=False):
        word1 = self.original_plugin.convert_word(word1)
        word2 = self.meaning_plugin.convert_word(word2)
        if word1 in self.direct_index and not may_overwrite:
            raise KeyError("This word already in dictionary: %s" % word1)
        self.direct_index[word1] = word2
        self.reverse_index[word2] = word1

    def _import_plugin(self, lang):
        try:
            module = __import__("%s.%s" % (self._PREFIX, lang),
                                fromlist=['create_plugin'])
        except ImportError:
            pass
        else:
            return module.create_plugin(self)
