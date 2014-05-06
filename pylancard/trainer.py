import logging
import random


DIRECT = 'direct'
REVERSE = 'reverse'
LOG = logging.getLogger(__name__)


class Trainer:

    def __init__(self, store, kind=DIRECT):
        self.store = store
        if kind == DIRECT:
            self._words = list(store.direct_index.items())
            self._plugin = store.meaning_plugin
        elif kind == REVERSE:
            self._words = list(store.reverse_index.items())
            self._plugin = store.original_plugin
        else:
            raise ValueError("Expected kind, got %r", kind)
        self.challenge = self.answer = None
        self._init()

    def check(self, answer):
        converted = self._plugin.convert_word(answer.strip())
        if converted != self.answer:
            LOG.info("'%(converted)s' (converted from '%(answer)s') "
                     "is incorrect",
                     locals())
            return False
        else:
            LOG.debug("%s is accepted", converted)
            return True

    def next(self):
        assert len(self._words) != 0
        try:
            self.challenge, self.answer = self._words[self._ptr]
        except IndexError:
            LOG.info("All words finished, starting from the beginning")
            self._init()
            return self.next()
        else:
            self._ptr += 1
        LOG.debug("Next challenge is '%s'", self.challenge)
        return self.challenge

    def _init(self):
        self._ptr = 0
        random.shuffle(self._words)
