import argparse
import logging
import os
import shlex
import sys

from . import store
from . import trainer
from . import utils


LOG = logging.getLogger(__name__)


HELP = """
Welcome to PyLancard, tool for learning words.

Commands:
> add word1=meaning1 word2="quoted meaning2"
  Adds words with their meaning to the dictionary.
  Will never overwrite anything.
> add! word1=meaning1 word2="quoted meaning2"
  The same as `add`, but will silently overwrite words.
> list
  List all words
> help
  Display this help
> quit
  Exit the program
> direct
  Start direct training mode (translate from foreign language)
> reverse
  Start reverse training mode (translate to foreign language)

When in training mode, commands are the following (note the slash):
> /quit
  Exit the training mode
> /skip
  Go to next word

Languages:
%(languages)s
"""


def add(command, store, arguments):
    try:
        words = utils.split_key_value(arguments)
    except ValueError as exc:
        print("ERROR: `add`: %s" % exc)
        return

    may_overwrite = command.endswith('!')
    for word, meaning in words:
        try:
            store.add_word(word, meaning, may_overwrite=may_overwrite)
        except KeyError as ex:
            print(str(ex))


def list_(command, store, arguments):
    for tpl in sorted(store.direct_index.items()):
        print("%s\t%s" % tpl)


def help_(command, store, arguments):
    languages = ['%s: %s' % (x.__class__.__name__, x.help_text)
                 for x in (store.original_plugin, store.meaning_plugin)
                 if x is not None]
    print(HELP % dict(languages='\n\n'.join(languages)))


def train(command, store, arguments):
    class Stop(Exception):
        @classmethod
        def stop(cls, *args):
            raise cls()

    tr = trainer.Trainer(store, command)

    def go_next(*args):
        challenge = tr.next()
        print("Next word: %s" % challenge)
        return challenge

    def check(word, *args):
        if not tr.check(word):
            print("Wrong, try again")
            return tr.challenge
        else:
            return go_next()

    train_commands = {
        '/quit': Stop.stop,
        '/skip': go_next,
        None: check,  # the default
    }

    go_next()
    try:
        run(store, train_commands, tr.challenge)
    except (Stop, SystemExit):
        pass


def run(store, commands_set, prompt=''):
    while True:
        try:
            line = input('%s > ' % prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        command, *arguments = shlex.split(line.strip())
        if not command:
            continue

        try:
            command, function = utils.matching_command(command, commands_set)
        except KeyError as exc:
            print(str(exc))
            print("Type ? for help")
            continue

        prompt = function(command, store, arguments) or ''


DEFAULT_COMMANDS = {
    'quit': lambda *_: sys.exit(0),
    '?': help_,
    'help': help_,
    'add': add,
    'add!': add,
    'list': list_,
    'direct': train,
    'reverse': train,
}


LANGUAGE_PROMPT = """Data file does not exists, create?
Input pair of languages (e.g. ru,cz) "
or empty string to quit> """


def main():
    import readline  # noqa

    parser = argparse.ArgumentParser(description="PyLanCard command line")
    parser.add_argument("filename", type=str, help="data file name")
    parser.add_argument("--debug", action='store_true', help="debug mode")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARN)

    if not os.path.exists(args.filename):
        languages = input(LANGUAGE_PROMPT)
        if not languages:
            sys.exit()
        languages = [s.strip() for s in languages.split(',')]
        store.create(args.filename, languages)

    with store.Store(args.filename) as store_file:
        if not store_file.original_plugin.present:
            LOG.warn("No plugin for language: %s", store_file.languages[0])
        if not store_file.meaning_plugin.present:
            LOG.warn("No plugin for language: %s", store_file.languages[1])

        run(store_file, DEFAULT_COMMANDS)


if __name__ == '__main__':
    main()
