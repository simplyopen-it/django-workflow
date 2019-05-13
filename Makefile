#!/usr/bin/env make -f

PYTHON=/usr/bin/env python
PY_PACKAGE_NAME=workflow
REPOSITORY="https://pypi.simplyopen.org"

.PHONY: all
all: sdist

.PHONY: clean
clean:
	rm -fr dist/* *.egg-info
	find . -name "*.pyc" -type f -exec rm -f {} +

sdist:
	$(PYTHON) setup.py sdist

upload:
	$(PYTHON) setup.py sdist upload --repository=$(REPOSITORY)

.PHONY: install
install:
	$(PYTHON) setup.py install
