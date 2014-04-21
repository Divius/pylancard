import random
import shlex
import sys


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


def train(command, store, arguments):
    challenge = expected = None
    words = list(store.direct_index.items())

    class Stop(Exception):
        @classmethod
        def stop(cls, *args):
            raise cls()

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
        run(store, train_commands, challenge)
    except Stop:
        pass


DEFAULT_COMMANDS = {
    'quit': lambda *_: sys.exit(0),
    '?': help_,
    'help': help_,
    'add': add,
    'add!': add,
    'list': list_,
    'train': train,
}


def matching_command(command, commands_set):
    candidates = {name: function
                  for (name, function) in commands_set.items()
                  if name is not None and name.startswith(command.strip())}
    if len(candidates) == 1:
        return next(iter(candidates.values()))
    elif command in candidates:
        return candidates[command]
    elif not candidates and None in commands_set:
        return commands_set[None]
    else:
        if not candidates:
            print("No such command: %s" % command)
        else:
            print("Ambiguous command %s, candidates are %s" %
                  (command, ', '.join(x[0] for x in candidates)))
        print("Type ? for help")


def run(store, commands_set=None, prompt=''):
    commands_set = commands_set or DEFAULT_COMMANDS
    while True:
        try:
            line = input('%s > ' % prompt)
        except EOFError:
            print()
            sys.exit(0)
        command, *arguments = shlex.split(line.strip())
        if not command:
            continue
        function = matching_command(command, commands_set)
        if function is not None:
            prompt = function(command, store, arguments) or ''
