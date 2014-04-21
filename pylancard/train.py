import random

from . import loop


class Stop(Exception):
    @classmethod
    def stop(cls, *args):
        raise cls()


def train(command, store, arguments):
    challenge = expected = None
    if command == 'direct':
        words = list(store.direct_index.items())
        plugin = store.meaning_plugin
    elif command == 'reverse':
        words = list(store.reverse_index.items())
        plugin = store.original_plugin
    else:
        print("ERROR: unknown training mode %s" % command)
        return

    def go_next(*args):
        nonlocal challenge, expected
        challenge, expected = random.choice(words)
        print("Next word: %s" % challenge)
        return challenge

    def check(word, *args):
        word = plugin.convert_word(word)
        if word != expected:
            print("Wrong, try again" + word)
            return challenge
        else:
            return go_next()

    train_commands = {
        '/quit': Stop.stop,
        '/skip': go_next,
        None: check,  # the default
    }

    go_next()
    try:
        loop.run(store, train_commands, challenge)
    except (Stop, SystemExit):
        pass
