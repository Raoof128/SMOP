.PHONY: install lint test format run e2e

install:
python -m venv .venv
. .venv/bin/activate && pip install -r requirements-dev.txt

lint:
ruff check .
black --check .

format:
black .
ruff check --fix .
echo "Formatting complete"

test:
pytest

run:
uvicorn backend.main:app --reload

e2e:
make lint
make test

