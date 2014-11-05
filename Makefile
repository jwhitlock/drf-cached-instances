.PHONY: clean-pyc clean-build clean-test clean-pyc clean docs

help:
	@echo "clean - remove all artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "lint - check style with flake8"
	@echo "qa - run linters and test coverage"
	@echo "qa-all - run QA plus tox, docs, and packaging"
	@echo "release - package and upload a release"
	@echo "sdist - package"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"

clean: clean-build clean-pyc clean-test

qa: lint coverage jslint

qa-all: qa docs sdist test-all

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 .

jslint:
	if type jslint >/dev/null 2>&1 ; then jslint drf_cached_instances/static/js/*; else echo "jslint not installed. To install node and jshint, use 'make install_jslint"; fi

install_jslint:
	if [ -z "$$VIRTUAL_ENV" ]; then echo "Run inside a virtualenv"; exit 1; fi
	mkdir -p .node_src_tmp
	cd .node_src_tmp && curl http://nodejs.org/dist/node-latest.tar.gz | tar xvz && cd node-v* && ./configure --prefix=$$VIRTUAL_ENV && make install
	npm install -g jslint
	rm -rf .node_src_tmp

test:
	./manage.py test

test-all:
	tox

coverage:
	coverage erase
	coverage run --source drf_cached_instances setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

sdist: clean
	python setup.py sdist
	ls -l dist
	check-manifest
	pyroma dist/`ls -t dist | head -n1`