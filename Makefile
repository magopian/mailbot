.PHONY: docs test clean

bin/python:
	virtualenv . --python python2
	bin/pip install -U setuptools
	bin/python setup.py develop

test: bin/python
	bin/pip install tox
	bin/tox

livetest: bin/python
	bin/pip install tox
	bin/tox -e py27-live,py33-live

docs:
	bin/pip install sphinx
	SPHINXBUILD=../bin/sphinx-build $(MAKE) -C docs html $^

clean:
	rm -rf bin .tox include/ lib/ man/ mailbot.egg-info/ build/
