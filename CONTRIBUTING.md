# Contributing to MD_Judge_Agent_Plugin

Thank you for your interest in contributing! **MD_Judge_Agent_Plugin** is a Python package that wraps the `MD_Judge` custom LLM agent, providing a CLI and library for evaluating `MD_Test` outputs, scoring them on a 0–10 rubric, and saving timestamped scoring artifacts. Contributions that improve reliability, extend the CLI, or add test coverage are especially welcome.

---

## 1. Development Environment Setup

### Prerequisites

- Python ≥ 3.11
- `git`
- A virtual environment tool (e.g., `venv` or `conda`)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Copilot-GitmobileLIVE/MD_Judge_test1.git
cd MD_Judge_test1

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the package in editable mode with development dependencies
pip install -e .
```

> The `md-judge-agent` CLI command will be available immediately after the editable install.

---

## 2. Running the Test Suite

Tests live in the `tests/` directory and use Python's built-in `unittest` framework.

```bash
# Run all tests
python -m pytest tests/

# Or with the standard library runner
python -m unittest discover -s tests
```

All tests must pass before a pull request can be merged.

---

## 3. Coding Guidelines

### Style

- Follow **[PEP 8](https://peps.python.org/pep-0008/)** for formatting and naming conventions.
- Maximum line length: **88 characters** (consistent with Black defaults).
- Use `snake_case` for functions and variables, `PascalCase` for classes.

### Docstrings

- Every public module, class, and function **must** have a docstring.
- Follow **[PEP 257](https://peps.python.org/pep-0257/)** conventions.

```python
def score_output(output: str, rubric: dict) -> int:
    """Evaluate an MD_Test output against a scoring rubric.

    Args:
        output: The raw text produced by MD_Test.
        rubric: A dict mapping criterion names to max point values.

    Returns:
        An integer score in the range 0–10.
    """
```

### Tests

- **Add tests for every new feature or bug fix** inside `tests/`.
- Name test files `test_<module>.py` and test methods `test_<behaviour>`.
- Aim for each test to cover a single, clearly named behaviour.
- Do not commit code that causes existing tests to fail.

### Commits

- Write clear, imperative commit messages (e.g., `Add scoring artifact timestamp`).
- Keep commits focused; avoid mixing unrelated changes.

---

## 4. Submitting a Pull Request

1. **Fork** the repository and create a feature branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding guidelines above.

3. Ensure the full test suite passes locally:

   ```bash
   python -m pytest tests/
   ```

4. **Push** your branch and open a pull request against `main`:

   ```bash
   git push origin feature/your-feature-name
   ```

5. In your PR description:
   - Summarise **what** changed and **why**.
   - Reference any related issues (e.g., `Closes #42`).
   - Note any manual testing steps reviewers should try.

6. A maintainer will review your PR. Please respond to feedback promptly. Once approved, your changes will be merged.

---

## Questions?

Open an [issue](https://github.com/Copilot-GitmobileLIVE/MD_Judge_test1/issues) or start a discussion — we're happy to help.
