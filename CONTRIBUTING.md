# Contributing to Unified Commerce Lakehouse

First off, thank you for considering contributing to this project. We welcome contributions from the community — whether it's a bug fix, a new feature, or an improvement to documentation.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)

---

## Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainer.

---

## Getting Started

### 1. Fork the Repository

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/DataLakehouse-Platform.git
cd DataLakehouse-Platform
```

### 2. Set Up Upstream Remote

```bash
git remote add upstream https://github.com/ojeshwigautam/DataLakehouse-Platform.git
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 5. Install Pre-commit Hooks

```bash
pre-commit install
```

---

## Development Workflow

### Branch Naming

Use the following branch naming conventions:

| Prefix | Purpose |
|--------|---------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `docs/` | Documentation changes |
| `refactor/` | Code refactoring |
| `test/` | Adding or updating tests |
| `chore/` | Maintenance tasks |

### Branch Convention

```bash
git checkout -b feat/your-feature-name
git checkout -b fix/your-bug-fix
git checkout -b docs/update-readme
```

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Examples:**

```
feat(silver): add schema evolution handling
fix(bronze): correct date parsing for edge cases
docs(readme): update installation instructions
test(gold): add regression tests for daily_sales
```

---

## Coding Standards

### Python

- **Formatting:** Code must pass `black --check .` (line length 88)
- **Import Order:** Sorted with `isort --profile=black --line-length=88`
- **Linting:** Must pass `ruff check .` with no errors
- **Type Hints:** All function signatures must include type annotations
- **Docstrings:** Google-style docstrings for all public modules, classes, and functions

### Pre-commit Hooks

The repository is configured with pre-commit hooks that automatically check:

| Hook | Purpose |
|------|---------|
| **Black** | Auto-formats Python code to consistent style |
| **isort** | Sorts imports in standard order |
| **Ruff** | Lints code and auto-fixes common issues |

Run against all files:

```bash
pre-commit run --all-files
```

---

## Testing Guidelines

### Running Tests

```bash
# Run the full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/regression/ -v
```

### Writing Tests

- Place tests in the `tests/` directory, mirroring the `src/` structure
- Use descriptive test names that explain the scenario being tested
- Include both positive and negative test cases
- Mock external services (database, Spark) where appropriate
- Add regression tests for critical pipeline paths

### Test Coverage

All new code should maintain at least 80% test coverage. The CI pipeline enforces this threshold.

---

## Pull Request Process

1. **Create a feature branch** from `develop`:
   ```bash
   git checkout -b feat/your-feature develop
   ```

2. **Make your changes**, following the coding standards above.

3. **Write or update tests** to cover your changes.

4. **Run all checks locally** before committing:
   ```bash
   black --check .
   isort --check-only --profile=black --line-length=88 .
   ruff check .
   pytest tests/ -v --cov=src --cov-report=term-missing
   ```

5. **Commit your changes** using conventional commit messages:
   ```bash
   git commit -m "feat(silver): add deduplication by order_unique_id"
   ```

6. **Push to your fork** and open a Pull Request:
   ```bash
   git push origin feat/your-feature
   ```

7. **Ensure CI passes** — all checks (lint, tests, Docker build, Terraform validation) must succeed.

8. **Request review** from a maintainer. Address any feedback.

9. **Merge** once approved. The maintainer will squash-merge into `develop`.

---

## Documentation

### When to Update Docs

- Every new feature must include corresponding documentation
- Changes to existing functionality require updates to affected docs
- README changes for new setup steps or configuration options

### Documentation Format

- All documentation is written in Markdown (`.md`)
- Use Mermaid for diagrams (fully supported on GitHub)
- Keep language clear, technical, and concise
- Include code examples for installation and usage

### Documentation Checklist

- [ ] Updated README.md if user-facing behavior changed
- [ ] Updated relevant docs in `docs/` directory
- [ ] API changes documented with correct signatures
- [ ] Configuration changes reflected in `.env.example`
- [ ] Docker/installation instructions updated if applicable

---

## Questions?

Open a [GitHub Discussion](https://github.com/ojeshwigautam/DataLakehouse-Platform/discussions) or reach out to the maintainer directly.

---

> **Thank you for contributing to the Unified Commerce Lakehouse!**

