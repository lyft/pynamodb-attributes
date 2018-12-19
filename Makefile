.PHONY: test
test:
	py.test tests/

.PHONY: lint
lint:
	pre-commit run --all-files --show-diff-on-failure
