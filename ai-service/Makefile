.PHONY: help install test lint format build run stop restart clean docker-build docker-run docker-stop docker-restart deploy test-all

PYTHON := python3
PIP := pip3
VENV := venv

help:
	@echo "AI Service - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install        - Install dependencies"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linters"
	@echo "  format         - Format code"
	@echo "  build          - Build Docker image"
	@echo "  run            - Run the application"
	@echo "  stop           - Stop the application"
	@echo "  restart        - Restart the application"
	@echo "  clean          - Clean up temporary files"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-stop    - Stop Docker container"
	@echo "  docker-restart - Restart Docker container"
	@echo "  deploy         - Deploy to server"
	@echo "  test-all       - Run all tests and linting"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov pytest-asyncio black flake8 bandit safety

test:
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

test-all:
	pytest tests/ -v --cov=. --cov-report=term-missing
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check .

format:
	black .

security:
	pip install safety bandit
	safety check || true
	bandit -r . -f json -o bandit_report.json || true

build:
	docker build -t ai-service:latest .

run:
	$(PYTHON) start_service.py

stop:
	pkill -f "uvicorn app.core.app:app" || true

restart: stop run

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf bandit_report.json

docker-build:
	docker build -t ai-service:latest .

docker-run:
	docker run -d --name ai-service -p 8001:8001 \
		-v $(shell pwd)/data:/app/data \
		-v $(shell pwd)/logs:/app/logs \
		-e REDIS_HOST=host.docker.internal \
		ai-service:latest

docker-stop:
	docker stop ai-service || true
	docker rm ai-service || true

docker-restart: docker-stop docker-run

docker-logs:
	docker logs -f ai-service

deploy:
	@echo "Deploying to server..."
	ssh $(DEPLOY_USER)@$(DEPLOY_HOST) "cd /opt/ai-service && git pull && docker-compose up -d --build"
	@echo "Deployment complete!"

deploy-staging:
	@echo "Deploying to staging..."
	ssh $(DEPLOY_USER)@$(STAGING_HOST) "cd /opt/ai-service && git pull && docker-compose up -d --build"
	@echo "Staging deployment complete!"
