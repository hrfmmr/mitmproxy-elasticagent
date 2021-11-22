.PHONY: testw
testw:
	arelo -d 2s -t 'oasdumper' -t 'tests' -p '**/*.py' -i '.venv' -i '.tmp' -i '.pytest_cache' -- make test

.PHONY: watch
watch:
	arelo -p 'main.py' -i '.venv' -i '.tmp' -i '.pytest_cache' -- make run

.PHONY: run
run:
	.venv/bin/python main.py

.PHONY: test
test:
	.venv/bin/pytest

.PHONY: preview
preview:
	open --new -a "Google Chrome" --args --new-window $(PWD)/.bundle/index.html
