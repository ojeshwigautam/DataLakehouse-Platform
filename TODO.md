# Milestone 4 — CI/CD & Developer Experience

## Steps

- [x] Plan approved
- [x] **1. Create `requirements-dev.txt`** (black, ruff, isort, pre-commit)
- [x] **2. Update `requirements.txt`** (remove pytest, pytest-cov → pure runtime)
- [x] **3. Create `.coveragerc`** (source paths, omit patterns)
- [x] **4. Update `pytest.ini`** (add `addopts` referencing coverage config)
- [x] **5. Create `.pre-commit-config.yaml`** (Black, isort, Ruff hooks)
- [x] **6. Update `.gitignore`** (add htmlcov/, .ruff_cache/, .mypy_cache/, etc.)
- [x] **7. Rewrite `.github/workflows/ci.yml`** (full pipeline with linting, tests, coverage, Docker build, Terraform)
- [x] **8. Update `README.md`** (badges + dev workflow documentation)

