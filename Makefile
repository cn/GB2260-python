PYTHON := python
PYTEST := py.test
TOX := tox

.PHONY: all build test test-all clean

all: build

build: gb2260/data/__init__.py
	$(PYTHON) setup.py sdist bdist_wheel

test: gb2260/data/__init__.py
	$(PYTEST)

test-all: gb2260/data/__init__.py
	$(TOX)

clean:
	rm -rf dist build gb2260/data/

gb2260/data/__init__.py: data/revisions.json
	$(PYTHON) generate.py $?

data/GB2260*.txt:
	git submodule init
	git submodule update
