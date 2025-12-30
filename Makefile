.PHONY: help clean cloc readme \
        pre-commit-run ty lint format \
        install nuke publish test

CLOC := cloc

#########
# UTILS #
#########

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

clean: ## Remove caches and compiled files
	@find . -path './.venv' -prune -o -type f -name "*.pyc" -delete
	@find . -path './.venv' -prune -o -type d -name "__pycache__" -exec rm -rf {} +
	@find . -path './.venv' -prune -o -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -path './.venv' -prune -o -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -path './.venv' -prune -o -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	@find . -path './.venv' -prune -o -type d -name "htmlcov" -exec rm -rf {} +

cloc: ## Show code statistics using cloc
	@echo "Code statistics using cloc:"
	$(CLOC) --exclude-dir=.venv,venv .

########
# LINT #
########

pre-commit-run: ## Run all pre-commit hooks
	uv run pre-commit run --all-files

ty: ## Run type checks
	uv run ty check . -v

lint: ty ## Run linting (type-check + ruff)
	uv run ruff format . --check
	uv run ruff check .
	@$(MAKE) --no-print-directory clean

format: pre-commit-run ## Auto-format code and fix lint issues
	uv run ruff format .
	uv run ruff check . --fix
	@$(MAKE) --no-print-directory clean

########
# UV   #
########

uv.lock:
	uv lock --check || uv lock

install: uv.lock ## Install project dependencies with uv
	uv sync --all-extras
	@$(MAKE) --no-print-directory clean

nuke: ## Remove virtualenv and reinstall dependencies from scratch
	uv clean
	rm -rf .venv
	@$(MAKE) --no-print-directory install

##########
# PYTEST #
##########

test: ## Run tests with coverage
	uv run pytest -vv --cov=src --cov-report=html
	@$(MAKE) --no-print-directory clean
