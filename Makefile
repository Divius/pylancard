FILE?=${HOME}/.pylancard
COVERAGE_GOAL?=70

run: test
	env/bin/python -m pylancard.cli --debug ${FILE}

test:
	env/bin/flake8 pylancard
	env/bin/coverage run --branch --include "pylancard*" -m unittest discover pylancard
	env/bin/coverage report -m --fail-under ${COVERAGE_GOAL}

env:
	rm -rf env
	virtualenv -p python3 env
	env/bin/pip install flake8 mock coverage

.PHONY: run test env
