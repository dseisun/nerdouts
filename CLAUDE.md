# Nerdouts Project Context

## Overview
Nerdouts is a fitness/workout management application that generates customizable workouts with voice guidance and music integration. It supports both dynamic workouts (generated based on time and category weights) and static pre-defined routines.

## Key Features
- **Dynamic Workouts**: Auto-generated based on time constraints and exercise category weights
- **Static Workouts**: Pre-defined routines stored in code or database
- **Exercise Management**: CRUD operations for exercises via web UI
- **Voice Guidance**: Text-to-speech announcements during workouts
- **Music Integration**: Spotify control (pause during announcements)
- **Web Interface**: FastAPI backend with HTML/JS frontend

## Tech Stack
- **Backend**: Python with FastAPI
- **Database**: SQLAlchemy ORM (PostgreSQL/MySQL/SQLite)
- **Frontend**: HTML templates with Jinja2, vanilla JavaScript
- **Real-time**: WebSockets for workout execution
- **Audio**: System TTS (macOS 'say' command), Spotify API

## Important Model Mappings
The Exercise model uses specific field names that differ from typical naming:
- `category_id` (not `category`) - Enum field for exercise category
- `long_desc` (not `description`) - Text description
- `default_time` (not `time_per_set`) - Time in seconds
- `repetition` (not `reps`) - Number of repetitions
- `side` - Must be one of: "Null", "Both", "Left", "Right" (never empty/None)
- `prompt` - Voice announcement template

## Exercise Categories
- `physical_therapy`
- `stretch`
- `strength`
- `rolling`

## Database Constraints
- All text fields require non-NULL values (use empty string "" if no value)
- `side` field defaults to "Null" for non-side-specific exercises
- `repetition` defaults to 1 if not specified

## Running the Application
```bash
# Web server
python -m nerdouts.web

# With debug mode
python -m nerdouts.web --debug
```

## Project Structure
- `/nerdouts/web.py` - Main FastAPI application and routes
- `/nerdouts/models.py` - SQLAlchemy models
- `/nerdouts/templates/` - HTML templates
- `/nerdouts/static/` - Static assets (JS/CSS)
- `/nerdouts/exercises.json` - Default exercise database

## Recent Changes
- Added comprehensive exercise management UI accessible from home page
- Exercise form supports four side options: Null (none), Both, Left, Right
- Added contextual "Add New Exercise" buttons in workout creation flow
- Fixed field mapping issues between API and database models

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest nerdouts/test_exercise_api.py

# Run with coverage
pytest --cov=nerdouts

# Run specific test class or method
pytest nerdouts/test_exercise_api.py::TestExerciseAPI::test_create_exercise_full

# Run tests with verbose output
pytest -v
```

### Test Structure
- `test_exercise_api.py` - Comprehensive tests for exercise CRUD operations
  - Tests all API endpoints (/api/exercises)
  - Tests page routes (/exercises, /exercises/new, etc.)
  - Includes edge cases (duplicates, invalid data, etc.)
  - Tests database constraints and relationships

### Key Test Fixtures
- `test_db` - In-memory SQLite database for isolated testing
- `client` - FastAPI test client
- `sample_exercise` - Single exercise for basic tests
- `multiple_exercises` - Multiple exercises for complex scenarios

### What the Tests Cover
1. **GET /api/exercises** - List all exercises (empty/populated)
2. **POST /api/exercises** - Create exercises (minimal/full data, duplicates, invalid category)
3. **PUT /api/exercises/{id}** - Update exercises (valid/invalid, duplicate names)
4. **DELETE /api/exercises/{id}** - Delete exercises (valid/invalid, used in workouts)
5. **Side field handling** - All four options (Null, Both, Left, Right)
6. **Page routes** - Exercise management UI pages