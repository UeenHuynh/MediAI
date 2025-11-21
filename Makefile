# MediAI - Makefile for common operations
# Usage: make <target>

.PHONY: help install setup start stop restart logs test clean data agents

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "MediAI - ICU Risk Prediction Platform"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

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

# ============================================================================
# DOCKER SERVICES
# ============================================================================

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

# ============================================================================
# DATA OPERATIONS
# ============================================================================

data: ## Generate and load sample data
	python scripts/generate_sample_data.py
	python scripts/load_sample_data.py

data-generate: ## Generate sample data only
	python scripts/generate_sample_data.py

data-load: ## Load sample data into database
	python scripts/load_sample_data.py

# ============================================================================
# AGENT SYSTEM (NEW!)
# ============================================================================

agents-demo: ## Run agent system demo
	@echo "Running multi-agent system demo..."
	python run_agent_demo.py

agents-ingest: ## Run data ingestion with agents
	python agents/orchestrator.py full-pipeline

agents-transform: ## Run dbt transformations with agents
	python agents/orchestrator.py transform

agents-quality: ## Run quality checks with agents (requires --target-table)
	@echo "Usage: make agents-quality-check TABLE=raw.patients"

agents-quality-check: ## Run quality check on specific table
	python agents/orchestrator.py quality --target-table $(TABLE)

agents-status: ## Show agent execution logs
	@echo "Recent agent logs:"
	@tail -50 logs/agent_demo.log 2>/dev/null || echo "No agent logs yet. Run: make agents-demo"

# ============================================================================
# TESTING
# ============================================================================

test: ## Run tests
	pytest tests/ -v

test-api: ## Test API endpoints
	@echo "Testing API..."
	curl -X GET http://localhost:8000/health
	curl -X GET http://localhost:8000/api/v1/models/info

test-agents: ## Test agent system
	pytest tests/test_agents.py -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=api --cov=agents --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# ============================================================================
# DATABASE
# ============================================================================

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d mimic_iv

db-status: ## Show database status
	docker-compose exec postgres psql -U postgres -d mimic_iv -c "\dt raw.*"
	docker-compose exec postgres psql -U postgres -d mimic_iv -c "SELECT COUNT(*) FROM raw.patients;"

# ============================================================================
# DEVELOPMENT
# ============================================================================

clean: ## Clean up data and Docker volumes
	docker-compose down -v
	rm -rf data/sample/*.csv
	rm -rf logs/*.log

rebuild: ## Rebuild Docker images
	docker-compose build --no-cache

shell-api: ## Open shell in API container
	docker-compose exec api bash

dev-api: ## Run API in development mode (hot reload)
	cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-ui: ## Run Streamlit in development mode
	cd apps && streamlit run app.py --server.port 8501

format: ## Format code with black
	black api/ apps/ scripts/ tests/ agents/

lint: ## Lint code with flake8
	flake8 api/ apps/ scripts/ tests/ agents/

# ============================================================================
# COMPLETE WORKFLOWS
# ============================================================================

demo: setup agents-demo start ## Complete demo: setup + agents + start services
	@echo ""
	@echo "=========================================="
	@echo "✓ MediAI Demo Complete!"
	@echo "=========================================="
	@echo ""
	@echo "Services running:"
	@echo "  - UI:  http://localhost:8501"
	@echo "  - API: http://localhost:8000/docs"
	@echo ""
	@echo "Agents executed successfully!"
	@echo ""

reset: clean setup ## Reset everything (clean + setup)
	@echo "✓ System reset complete"
