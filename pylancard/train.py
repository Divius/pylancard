import random

from . import loop


class Stop(Exception):
    @classmethod
    def stop(cls, *args):
        raise cls()


def train(command, store, arguments):
    challenge = expected = None
    words = list(store.direct_index.items())

    def go_next(*args):
        nonlocal challenge, expected
        challenge, expected = random.choice(words)
        print("Next word: %s" % challenge)
        return challenge

    def check(word, *args):
        if word != expected:
            print("Wrong, try again")
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
    except Stop:
        pass
