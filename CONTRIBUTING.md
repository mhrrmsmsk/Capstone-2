# Contributing to Crop Recommendation & Yield Optimization System

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/crop-recommendation-system.git
   cd crop-recommendation-system
   ```
3. **Set up** the development environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install pytest ruff
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and add tests
3. Run the test suite:
   ```bash
   python -m pytest tests/ -v
   ```
4. Commit with a descriptive message
5. Push to your fork and open a Pull Request

## Code Style

- Follow **PEP 8** conventions
- Use **type hints** where practical
- Write **docstrings** for all public classes and methods
- Keep functions focused and modular
- Run linting before submitting:
  ```bash
  ruff check src/ tests/
  ```

## Reporting Issues

- Use [GitHub Issues](../../issues) to report bugs or request features
- Include:
  - Python version and OS
  - Steps to reproduce
  - Expected vs. actual behavior
  - Relevant logs or error messages

## Pull Request Guidelines

- **One feature per PR** — keep changes focused
- **Add tests** for new functionality
- **Update documentation** if you change behavior
- **Ensure all tests pass** before requesting review
- Reference any related issues in the PR description

## Project Structure

```
src/
├── preprocessing.py    # Data loading and feature engineering
├── train.py            # Model training and evaluation
├── predict.py          # Unified prediction engine
├── recommender.py      # KNN-based recommendation system
├── api.py              # FastAPI REST endpoints
└── logger.py           # Logging configuration

tests/
└── test_smoke.py       # Smoke tests

streamlit_app.py        # Web interface
run_pipeline.py         # End-to-end training pipeline
```

## Adding New Features

### New Model
1. Add training logic in `src/train.py`
2. Add prediction logic in `src/predict.py`
3. Add API endpoint in `src/api.py` (if applicable)
4. Add tests in `tests/`
5. Update `models/metadata.json` schema if needed

### New API Endpoint
1. Define Pydantic input/output models in `src/api.py`
2. Implement the endpoint with proper error handling
3. Add tests for the endpoint
4. Update README and API documentation

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
