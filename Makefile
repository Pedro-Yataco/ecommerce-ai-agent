DOCKER_COMPOSE := docker compose
API_SERVICE := api

.PHONY: run build down logs test lint format migrate migration load-data shell db-shell

run:
	$(DOCKER_COMPOSE) up --build

build:
	$(DOCKER_COMPOSE) build

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

test:
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) pytest

lint:
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) ruff check .
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) black --check .

format:
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) ruff check . --fix
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) black .

migrate:
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) alembic upgrade head

migration:
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) alembic revision --autogenerate -m "$(m)"

load-data:
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) python -m scripts.load_olist_data --data-dir data/raw/olist

shell:
	$(DOCKER_COMPOSE) run --rm $(API_SERVICE) bash

db-shell:
	$(DOCKER_COMPOSE) exec postgres psql -U postgres -d ecommerce_ai_agent