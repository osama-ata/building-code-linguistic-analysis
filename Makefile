.PHONY: setup lint test run-pipeline

setup:
	uv sync

lint:
	ruff check .
	mypy src scripts tests

test:
	pytest tests/ --cov=src

run-pipeline:
	python scripts/run_pipeline.py
