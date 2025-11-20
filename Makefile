# MediAI - Makefile for common operations
# Usage: make <target>

.PHONY: help install setup start stop restart logs test clean data

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "MediAI - ICU Risk Prediction Platform"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

setup: ## Initial setup (generate data + start services)
	@echo "Setting up MediAI..."
	python scripts/generate_sample_data.py
	docker-compose up -d postgres redis
	@echo "Waiting for database to be ready..."
	sleep 10
	python scripts/load_sample_data.py
	@echo "✓ Setup complete!"

start: ## Start all services
	docker-compose up -d
	@echo "Services starting..."
	@echo "  - API:       http://localhost:8000"
	@echo "  - UI:        http://localhost:8501"
	@echo "  - Postgres:  localhost:5432"
	@echo "  - Redis:     localhost:6379"

stop: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View API logs
	docker-compose logs -f api

logs-ui: ## View UI logs
	docker-compose logs -f streamlit

ps: ## Show running services
	docker-compose ps

health: ## Check service health
	@echo "Checking services..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "❌ API not responding"
	@docker-compose ps

test: ## Run tests
	pytest tests/ -v

test-api: ## Test API endpoints
	@echo "Testing API..."
	curl -X GET http://localhost:8000/health
	curl -X GET http://localhost:8000/api/v1/models/info

data: ## Generate and load sample data
	python scripts/generate_sample_data.py
	python scripts/load_sample_data.py

clean: ## Clean up data and Docker volumes
	docker-compose down -v
	rm -rf data/sample/*.csv
	rm -rf logs/*.log

rebuild: ## Rebuild Docker images
	docker-compose build --no-cache

shell-api: ## Open shell in API container
	docker-compose exec api bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d mimic_iv

dev-api: ## Run API in development mode (hot reload)
	cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-ui: ## Run Streamlit in development mode
	cd apps && streamlit run app.py --server.port 8501

format: ## Format code with black
	black api/ apps/ scripts/ tests/

lint: ## Lint code with flake8
	flake8 api/ apps/ scripts/ tests/
