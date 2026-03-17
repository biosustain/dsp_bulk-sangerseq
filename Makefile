PYTHON ?= python3

.PHONY: install-dev lint test check

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

lint:
	$(PYTHON) -m ruff check scripts tests

test:
	$(PYTHON) -m pytest -q

check: lint test
