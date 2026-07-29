.PHONY: dev lint typecheck test complexity deps coverage security runbooks docs validate

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
	.venv/bin/python3 -m pytest scripts/test-eval-validation.py scripts/test-eval-coverage.py eval_runner/tests/ -v --durations=10

test-integration:
	.venv/bin/python3 -m pytest tests/integration/ -v --durations=10

test-cov:
	.venv/bin/python3 -m pytest scripts/test-eval-validation.py scripts/test-eval-coverage.py eval_runner/tests/ tests/integration/ -v --durations=10 --cov=scripts --cov=eval_runner --cov-fail-under=60 --cov-report=term-missing

test-parallel:
	.venv/bin/python3 -m pytest scripts/test-eval-validation.py scripts/test-eval-coverage.py eval_runner/tests/ tests/integration/ -n auto -v --durations=10

# ─── Dependencies ───────────────────────────────────────────────
deps:
	.venv/bin/python3 -m deptry .

# ─── Security ───────────────────────────────────────────────────
security:
	.venv/bin/python3 -m bandit -r scripts/ -f txt --severity-level high

# ─── Documentation ──────────────────────────────────────────────
docs:
	ruby scripts/validate-skills.rb
	ruby scripts/validate-skill-quality.rb --base origin/main
	python3 scripts/test-eval-validation.py
	python3 scripts/validate-evals.py

# ─── Full Validation ────────────────────────────────────────────
validate: lint format-check typecheck complexity deps test-cov
	@echo "All checks passed."
