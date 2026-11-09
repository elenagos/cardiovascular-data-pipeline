.PHONY: install test coverage lint format quality analytics dashboard java-test precommit

install:
	uv sync

test:
	uv run pytest -v

coverage:
	uv run pytest --cov=analytics --cov-report=term-missing

lint:
	uv run ruff check .

format:
	uv run ruff format .

precommit:
	uv run pre-commit run --all-files

quality:
	uv run ruff check .
	uv run pytest -v

analytics:
	uv run python analytics/run_pipeline.py

dashboard:
	uv run streamlit run dashboard/app.py

java-test:
	mvn test

.PHONY: api api-test

api:
	uv run uvicorn api.main:app --reload

api-test:
	uv run pytest tests/test_api.py -v
integration-test:
	uv run pytest -m integration -v

unit-test:
	uv run pytest -m "not integration" -v

test-all:
	uv run pytest -v
