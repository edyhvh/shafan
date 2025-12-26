.PHONY: setup install clean

# Python executable to use (tries to use venv first)
PYTHON := .venv/bin/python
PIP := .venv/bin/pip

# Default target
all: setup

setup:
	@echo "🚀 Setting up shafan environment..."
	@python3 setup.py

install: setup

# Clean build artifacts
clean:
	rm -rf .venv
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the example script
example:
	@$(PYTHON) scripts/example_ocr.py

# Frontend commands
frontend-dev:
	@cd frontend && npm run dev

frontend-build:
	@cd frontend && npm run build

frontend-install:
	@cd frontend && npm install
