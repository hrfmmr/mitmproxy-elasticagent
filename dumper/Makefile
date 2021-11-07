.PHONY: testw
testw:
	.venv/bin/pytest-watch

.PHONY: watch
watch:
	arelo -p 'main.py' -i '.venv' -i '.tmp' -i '.pytest_cache' -- make run

.PHONY: run
run:
	.venv/bin/python main.py
