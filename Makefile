#!/usr/bin/env make -f

PYTHON=/usr/bin/env python
REPOSITORY="https://apt.simplyopen.org:8888"

.PHONY: all
all: sdist

.PHONY: clean
clean:
	rm -fr dist/* *.egg-info

sdist:
	$(PYTHON) setup.py sdist

upload:
	$(PYTHON) setup.py sdist upload --repository=$(REPOSITORY)

.PHONY: install
install:
	$(PYTHON) setup.py install
