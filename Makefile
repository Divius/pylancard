run: test
	env/bin/python -m pylancard ${FILE}

test:
	env/bin/flake8 pylancard

env:
	rm -rf env
	virtualenv -p python3 env
	env/bin/pip install flake8

.PHONY: test env
