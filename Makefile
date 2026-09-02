.PHONY: dev lint typecheck test complexity deps coverage security dep-age runbooks docs validate

# Keep local core tests aligned with the required CI coverage selection.
CORE_TESTS := $(shell cat scripts/core-test-files.txt)

# ─── Development Setup ──────────────────────────────────────────
dev: .venv
	@echo "Development environment ready. Run 'make validate' to run all checks."

.venv:
	python3 -m venv .venv
	.venv/bin/python3 -m pip install --upgrade pip
	.venv/bin/python3 -m pip install -r requirements-dev.txt
	@echo "Virtual environment created at .venv/"

# ─── Linting & Formatting ───────────────────────────────────────
lint:
	.venv/bin/python3 -m ruff check scripts/ eval_runner/

format-check:
	.venv/bin/python3 -m ruff format --check scripts/ eval_runner/

format:
	.venv/bin/python3 -m ruff format scripts/ eval_runner/

# ─── Type Checking ──────────────────────────────────────────────
typecheck:
	.venv/bin/python3 -m mypy scripts/ eval_runner/

# ─── Complexity ─────────────────────────────────────────────────
complexity:
	.venv/bin/python3 -m radon cc scripts/ eval_runner/ --min B --total-average

# ─── Testing ────────────────────────────────────────────────────
test:
	.venv/bin/python3 -m pytest $(CORE_TESTS) -v --durations=10

test-integration:
	.venv/bin/python3 -m pytest tests/integration/ -v --durations=10

test-cov:
	.venv/bin/python3 -m pytest $(CORE_TESTS) tests/integration/ -v --durations=10 --cov=scripts --cov=eval_runner --cov-fail-under=60 --cov-report=term-missing

test-parallel:
	.venv/bin/python3 -m pytest $(CORE_TESTS) -n auto -v --durations=10

# ─── Dependencies ───────────────────────────────────────────────
deps:
	.venv/bin/python3 -m deptry .

# ─── Security ───────────────────────────────────────────────────
security:
	.venv/bin/python3 -m bandit -r scripts/ -f txt --severity-level high

dep-age:
	.venv/bin/python3 scripts/check-dependency-age.py

# ─── Documentation ──────────────────────────────────────────────
docs:
	ruby scripts/validate-skills.rb
	ruby scripts/validate-skill-quality.rb --base origin/main
	python3 scripts/test-eval-validation.py
	python3 scripts/validate-evals.py

# ─── Full Validation ────────────────────────────────────────────
validate: lint format-check typecheck complexity deps dep-age test-cov
	@echo "All checks passed."
