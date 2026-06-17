up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	poetry run alembic upgrade head

makemigrations:
	poetry run alembic revision --autogenerate -m "$(m)"

run:
	poetry run uvicorn marketplace_blog.main:app --reload

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

test:
	poetry run pytest