import os
import readline  # noqa
import sys

from . import commands
from . import store


def usage():
    print("USAGE: {} <file name>".format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)


try:
    filename = sys.argv[1]
except IndexError:
    usage()

if not os.path.exists(filename):
    print("File does not exists, create?")
    languages = input("Input pair of languages (e.g. ru,cz) "
                      "or empty string to quit> ")
    if not languages:
        sys.exit()
    languages = [s.strip() for s in languages.split(',')]
    store.create(filename, languages)

with store.Store(filename) as store_file:
    if not store_file.original_plugin.present:
        print("No plugin for language: %s" % store_file.languages[0])
    if not store_file.meaning_plugin.present:
        print("No plugin for language: %s" % store_file.languages[1])
    commands.run_default(store_file)
