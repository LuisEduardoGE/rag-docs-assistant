PYTHON ?= python
PORT ?= 8000

.DEFAULT_GOAL := help
.PHONY: help install fetch index eval run test lint clean

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Install runtime and dev dependencies (pytest, ruff)
	$(PYTHON) -m pip install -r requirements-dev.txt

fetch: ## Download the FastAPI docs corpus into data/corpus (~18 MB)
	$(PYTHON) -m app.fetch_docs

index: ## Chunk, embed and write the LanceDB index (first run downloads the ~130 MB model)
	$(PYTHON) -m app.index

eval: ## Score vector, keyword and hybrid retrieval on both question sets
	$(PYTHON) -m evaluation.run_eval

run: ## Start the API and UI on 127.0.0.1 (PORT=8000 by default; needs the index)
	$(PYTHON) -m uvicorn app.api:app --reload --port $(PORT)

test: ## Run the test suite (no API key, no model download)
	$(PYTHON) -m pytest -q

lint: ## Ruff with default rules
	$(PYTHON) -m ruff check .

clean: ## Remove caches (keeps data/)
	rm -rf .pytest_cache .ruff_cache docs/rag-build-guide.html
	find . -name __pycache__ -type d -not -path './.venv/*' -prune -exec rm -rf {} +
