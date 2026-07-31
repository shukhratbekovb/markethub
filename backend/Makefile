dev:
	poetry run uvicorn src.main:app --reload
upgrade:
	poetry run alembic upgrade head
downgrade:
	poetry run alembic downgrade -1
run:
	poetry run uvicorn src.main:app --host="0.0.0.0" --port="8000"
