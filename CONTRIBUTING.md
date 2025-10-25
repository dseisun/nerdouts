# Contributing to Nerdouts

Thank you for your interest in contributing to Nerdouts! This document provides guidelines and instructions for development.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Database Management](#database-management)
- [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites
- Python 3.8 or higher (Python 3.11 recommended)
- System dependencies (Linux):
  ```bash
  sudo apt-get install libdbus-1-dev libdbus-glib-1-dev festival libssl-dev
  ```

### Initial Setup

**Quick Setup (Recommended)**
```bash
./scripts/dev_setup.sh
```

**Manual Setup**
1. Install the UV package manager:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   make dev-install
   ```

3. Create database configuration:
   ```bash
   cp nerdouts/secrets.yaml.template nerdouts/secrets.yaml
   # Edit secrets.yaml with your database credentials
   ```

4. Initialize the database:
   ```bash
   make init-db-full
   ```

## Development Workflow

### Available Commands

View all available commands:
```bash
make help
```

### Running the Application

**Start the web server:**
```bash
make run
```
The application will be available at `http://localhost:8000`

**Start with debug logging:**
```bash
make debug
```

### Project Structure

```
nerdouts/
├── nerdouts/              # Main package
│   ├── web.py            # FastAPI application (main entry point)
│   ├── models.py         # SQLAlchemy database models
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection setup
│   ├── init_db.py        # Database initialization
│   ├── templates/        # Jinja2 HTML templates
│   ├── static/           # CSS, JavaScript, assets
│   └── test_*.py         # Test files
├── scripts/              # Development helper scripts
├── Makefile              # Development task automation
├── pyproject.toml        # Project dependencies and configuration
└── pytest.ini            # Test configuration
```

## Code Quality

### Automated Checks

Run all quality checks at once:
```bash
make all-checks
```

This runs:
- Code formatting checks (black, ruff)
- Linting (ruff)
- Type checking (mypy)
- All tests

### Formatting

**Auto-format code:**
```bash
make format
```

**Check formatting without changes:**
```bash
make format-check
```

### Linting

```bash
make lint
```

### Type Checking

```bash
make type-check
```

Note: Type checking warnings won't fail CI initially but should be addressed over time.

## Testing

### Running Tests

**Run all tests:**
```bash
make test
```

**Run with coverage report:**
```bash
make test-cov
```

**Run specific test file:**
```bash
make test-file FILE=nerdouts/test_exercise_api.py
```

**Run specific test class or method:**
```bash
pytest nerdouts/test_exercise_api.py::TestExerciseAPI::test_create_exercise
```

**Verbose output:**
```bash
make test-verbose
```

### Writing Tests

- Place test files in the `nerdouts/` directory with the prefix `test_`
- Use pytest fixtures for common setup (see `test_exercise_api.py` for examples)
- Test files automatically use an in-memory SQLite database for isolation
- Aim for comprehensive coverage of new features

**Example test structure:**
```python
import pytest
from fastapi.testclient import TestClient

def test_example(client, test_db):
    """Test description."""
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

### Coverage Reports

After running `make test-cov`, view the HTML coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Database Management

### Initialize Database

**Create tables only:**
```bash
make init-db
```

**Create tables and load sample data:**
```bash
make init-db-full
```

**Reset database (drop and recreate):**
```bash
make reset-db
```

### Database Models

Key models are defined in `nerdouts/models.py`:
- `Exercise` - Individual exercises
- `Workout` - Workout sessions
- `StaticWorkout` - Pre-defined workout routines

**Important field mappings:**
- `category_id` (not `category`) - Exercise category enum
- `long_desc` (not `description`) - Text description
- `default_time` (not `time_per_set`) - Time in seconds
- `side` - Must be one of: "Null", "Both", "Left", "Right"

### Exercise Categories
- `physical_therapy`
- `stretch`
- `strength`
- `rolling`

## Submitting Changes

### Before Submitting

1. **Run all quality checks:**
   ```bash
   make all-checks
   ```

2. **Ensure tests pass:**
   ```bash
   make test-cov
   ```

3. **Update documentation** if you've changed:
   - API endpoints
   - Database models
   - Configuration options
   - User-facing features

### Commit Guidelines

- Write clear, descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic

**Example:**
```
Add exercise filtering by category

- Implement GET /api/exercises?category=strength endpoint
- Add dropdown filter to exercise management UI
- Add tests for category filtering

Fixes #123
```

### Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request with:
   - Clear description of changes
   - Related issue numbers
   - Screenshots (if UI changes)
   - Test coverage information

5. Ensure CI checks pass

6. Address review feedback

## Resetting Your Environment

If you need to start fresh:
```bash
./scripts/dev_reset.sh
```

This will:
- Clean cache files
- Remove database files
- Optionally reinitialize with sample data

## Getting Help

- Check existing documentation in `README.md` and `CLAUDE.md`
- Review existing tests for examples
- Open an issue for questions or bugs

## Code Style

- **Line length:** 100 characters
- **Python version:** Compatible with Python 3.8+
- **Formatting:** Automated with black and ruff
- **Imports:** Sorted with isort (via ruff)
- **Type hints:** Encouraged but not required

## Development Tips

1. **Hot reload:** uvicorn auto-reloads on file changes when running via `make run`
2. **Debug logging:** Use `make debug` for verbose logging
3. **Database inspection:** Check `secrets.yaml` for database connection strings
4. **API documentation:** Visit `/docs` when running the server for interactive API docs
5. **Quick iteration:** Use `./scripts/quick_test.sh test_file.py` for rapid testing

## Architecture Notes

- **Backend:** FastAPI with async support
- **Frontend:** Server-side rendered Jinja2 templates with vanilla JavaScript
- **Database:** SQLAlchemy ORM (supports SQLite, PostgreSQL, MySQL)
- **Real-time:** WebSockets for workout execution
- **Audio:** Client-side TTS via Web Speech API
- **Music:** Spotify Web SDK integration

## Common Tasks

**Add a new exercise category:**
1. Update `category_id` enum in `models.py`
2. Update `config.json` with category weight
3. Add tests for the new category

**Add a new API endpoint:**
1. Add route to `web.py`
2. Add corresponding tests in `test_*.py`
3. Update API documentation

**Modify database schema:**
1. Update models in `models.py`
2. Consider migration strategy (manual for now)
3. Update `init_db.py` if needed
4. Add tests for schema changes

---

Thank you for contributing to Nerdouts! 🎉
