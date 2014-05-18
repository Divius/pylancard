import gzip
import json
import logging

from .plugins import base


LOG = logging.getLogger(__name__)


def create(filename, languages):
    LOG.info("Creating store %(filename)s for languages %(languages)s",
             locals())
    with gzip.open(filename, 'wb') as fp:
        fp.write(json.dumps({'languages': languages,
                             'index': {},
                             'version': 1},
                            fp, indent=2).encode('utf-8'))


class Store(dict):

    _PREFIX = 'pylancard.plugins'

    def __init__(self, filename):
        super().__init__()
        self._filename = filename
        with gzip.open(filename, 'rb') as fp:
            self.update(json.loads(fp.read().decode('utf-8')))
            LOG.info("Opened store %(filename)s of version %(version)s",
                     dict(filename=filename, version=self.get('version')))

        self.languages = tuple(self['languages'])
        LOG.info("Languages: %s", self.languages)
        self.direct_index = self['index']
        self.reverse_index = {v: k for (k, v) in self.direct_index.items()}
        self.original_plugin = (self._import_plugin(self.languages[0])
                                or base.BaseLanguage(self))
        LOG.info("Class of original language plugin: %s",
                 self.original_plugin.__class__)
        self.meaning_plugin = (self._import_plugin(self.languages[1])
                               or base.BaseLanguage(self))
        LOG.info("Class of meaning language plugin: %s",
                 self.meaning_plugin.__class__)

    def save(self):
        self['index'] = self.direct_index
        with gzip.open(self._filename, 'wb') as fp:
            fp.write(json.dumps(self, indent=2).encode('utf-8'))

    close = save

    __enter__ = lambda self: self

    def __exit__(self, *_):
        self.save()

    def add(self, word1, word2, may_overwrite=False):
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
