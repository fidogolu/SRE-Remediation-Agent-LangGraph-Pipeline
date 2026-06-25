# =============================================================================
# Makefile — langgraph-pipeline-template
# =============================================================================

.PHONY: help run test lint dev docker-build docker-clean clean

help: ## Show available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

run: ## Run the pipeline with default paths
	uv run main.py

run-custom: ## Run with custom input/output paths
	uv run main.py --input $(INPUT) --output $(OUTPUT)

test: ## Run all tests
	uv run pytest -v

test-cov: ## Run tests with coverage report
	uv run pytest --cov=. --cov-report=html --cov-report=term

lint: ## Run flake8 linter
	flake8 .

format: ## Auto-format code with ruff (if available)
	uv run ruff format .

check: ## Run test + lint
	$(MAKE) test
	$(MAKE) lint

docker-build: ## Build Docker image
	docker-compose build

docker-run: ## Run Docker container
	docker-compose up app

docker-test: ## Run tests in Docker
	docker-compose run tests

docker-clean: ## Remove Docker images and volumes
	docker-compose down -v
	docker image prune -f

clean: ## Remove cache and build artifacts
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf logs/*
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +

setup: ## Install dependencies and create .env
	uv sync
	cp .env.example .env
	@echo "Setup complete. Edit .env with your configuration."
