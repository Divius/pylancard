[![Build Status](https://travis-ci.org/Divius/pylancard.svg?branch=master)](https://travis-ci.org/Divius/pylancard)

# PyLanCard

pylancard is a very simple console tool for language learning.
pylancard is written in Python and supports versions >= 3.2.

Install:

    git clone https://github.com/Divius/pylancard
    cd pylancard
    make env

Test:

    make test

Until we have proper scripts, run with:

    make

or you may set path to data file:

    make FILE=/path/to/file

or you can run just program without running tests:

    make run

First time you run, you will be asked for a pair of languages to use.
Input e.g. "cz,ru" to translate from Czech to Russian.
Some languages have special support (composition feature), currently:
- cz (Czech)

Type "help" for list of commands.
