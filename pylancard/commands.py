import sys

from . import loop
from . import train


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

When in training mode, commands are the following (note the slash):
> /quit
  Exit the training mode
> /skip
  Go to next word

Languages:
%(languages)s
"""


def add(command, store, arguments):
    words = [tuple(y.strip()
                   for y in x.strip().split('=', 1))
             for x in arguments
             if x.strip()]
    if not words:
        print("ERROR: at least one argument required for `add`")
        return

    bad_format = [x[0] for x in words if len(x) < 2]
    if bad_format:
        print("ERROR: meaning required for words: %s" % ', '.join(bad_format))
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


DEFAULT_COMMANDS = {
    'quit': lambda *_: sys.exit(0),
    '?': help_,
    'help': help_,
    'add': add,
    'add!': add,
    'list': list_,
    'train': train.train,
}


def run_default(store):
    loop.run(store, DEFAULT_COMMANDS)
