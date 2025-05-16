SHELL := /bin/bash

.PHONY: help setup install run test docker docker-build docker-run docker-stop clean

help:
	@echo "Available commands:"
	@echo "  setup         - Create virtual environment and install dependencies"
	@echo "  install       - Install dependencies"
	@echo "  run           - Run the API server"
	@echo "  test          - Run tests"
	@echo "  docker        - Build and run with Docker"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run with Docker"
	@echo "  docker-stop   - Stop Docker containers"
	@echo "  clean         - Remove virtual environment and cached files"

setup:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Installing dependencies..."
	source venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete. Activate virtual environment with 'source venv/bin/activate'"

install:
	pip install -r requirements.txt

run:
	@if [ -f .env ]; then \
		export $$(cat .env | xargs) && python server.py; \
	else \
		echo ".env file not found. Using default environment variables."; \
		python server.py; \
	fi

test:
	pytest tests.py -v

docker: docker-build docker-run

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

clean:
	rm -rf venv
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name ".eggs" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type f -name ".coverage.*" -delete
