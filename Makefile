# ppt-lint Makefile
.PHONY: init test lint verify clean help install

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Initialize development environment
	@echo "🛠️  Initializing Development Environment..."
	pip install -e ".[dev]"
	@echo "✅ Done! Environment is ready."

install: ## Install ppt-lint
	pip install -e .

test: ## Run tests
	@echo "🧪 Running Tests..."
	pytest tests/ -v --tb=short
	@echo "✅ Tests passed."

lint: ## Run linters
	@echo "🔍 Running Linters..."
	ruff check .
	ruff format --check .
	@echo "✅ Lint check passed."

verify: lint test ## Full verification
	@echo "🛡️  Full System Verification Passed."

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .ppt-lint-cache/
