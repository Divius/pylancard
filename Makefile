FILE?=${HOME}/.pylancard

run: test
	env/bin/python -m pylancard ${FILE}

test:
	env/bin/flake8 pylancard
	env/bin/python -m unittest discover pylancard

env:
	rm -rf env
	virtualenv -p python3 env
	env/bin/pip install flake8 mock

.PHONY: run test env
