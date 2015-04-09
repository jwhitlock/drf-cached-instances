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

qa: lint coverage

qa-all: qa docs sdist test-all

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . \( ! -name .tox \) -name '*.pyc' -exec rm -f {} +
	find . \( ! -name .tox \) -name '*.pyo' -exec rm -f {} +
	find . \( ! -name .tox \) -name '*~' -exec rm -f {} +
	find . \( ! -name .tox \) -name '__pycache__' -exec rm -f -R {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 .

test:
	./manage.py test

test-all:
	tox --skip-missing-interpreters

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
	python setup.py sdist bdist_wheel upload
	python -m webbrowser -n https://pypi.python.org/pypi/drf-cached-instances

test-release: sdist
	python setup.py register -r https://testpypi.python.org/pypi
	python setup.py sdist bdist_wheel upload -r https://testpypi.python.org/pypi
	python -m webbrowser -n https://testpypi.python.org/pypi/drf-cached-instances

sdist: clean
	python setup.py sdist
	ls -l dist
	check-manifest
	pyroma dist/`ls -t dist | head -n1`
