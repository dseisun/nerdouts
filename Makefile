.PHONY: help install dev-install run debug test test-cov test-verbose init-db lint format type-check clean all-checks

# Default target
help:
	@echo "Nerdouts Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install         Install production dependencies"
	@echo "  make dev-install     Install development dependencies"
	@echo ""
	@echo "Running the Application:"
	@echo "  make run             Run the web server (localhost:8000)"
	@echo "  make debug           Run with debug logging enabled"
	@echo ""
	@echo "Database Management:"
	@echo "  make init-db         Initialize database schema"
	@echo "  make init-db-full    Initialize database with exercises and static workouts"
	@echo "  make reset-db        Reset database (drops and recreates)"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make test-verbose    Run tests with verbose output"
	@echo "  make test-file FILE= Run specific test file"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Run linting checks (ruff)"
	@echo "  make format          Auto-format code (ruff + black)"
	@echo "  make format-check    Check formatting without changes"
	@echo "  make type-check      Run type checking (mypy)"
	@echo "  make all-checks      Run all quality checks (lint, format-check, type-check, test)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           Remove build artifacts and cache files"
	@echo "  make clean-db        Remove local database files"

# Installation
install:
	uv sync

dev-install:
	uv sync --all-extras
	uv pip install pytest pytest-cov ruff black mypy

# Running
run:
	python -m nerdouts.web

debug:
	python -m nerdouts.web --debug

# Database
init-db:
	python -m nerdouts.init_db

init-db-full:
	python -m nerdouts.init_db --exercises nerdouts/exercises.json --static-workouts

reset-db:
	python -m nerdouts.init_db --force --exercises nerdouts/exercises.json --static-workouts

# Testing
test:
	pytest

test-cov:
	pytest --cov=nerdouts --cov-report=term-missing --cov-report=html

test-verbose:
	pytest -v

test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE parameter required. Usage: make test-file FILE=path/to/test.py"; \
		exit 1; \
	fi
	pytest $(FILE) -v

# Code Quality
lint:
	@echo "Running ruff linter..."
	ruff check nerdouts/

format:
	@echo "Formatting code with ruff..."
	ruff check --fix nerdouts/
	@echo "Formatting code with black..."
	black nerdouts/

format-check:
	@echo "Checking code format with ruff..."
	ruff check nerdouts/
	@echo "Checking code format with black..."
	black --check nerdouts/

type-check:
	@echo "Running mypy type checker..."
	mypy nerdouts/ --ignore-missing-imports

all-checks: format-check lint type-check test
	@echo ""
	@echo "✅ All checks passed!"

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	@echo "✅ Cleanup complete"

clean-db:
	@echo "Removing local database files..."
	find . -type f -name "*.db" -delete
	@echo "✅ Database files removed"
