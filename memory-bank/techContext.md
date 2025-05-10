# Technical Context: Nerdouts

## Technology Stack

### Backend
- **Python**: Core programming language (3.8+)
- **FastAPI**: Web framework for API and UI
- **SQLAlchemy**: ORM for database operations
- **Uvicorn**: ASGI server for FastAPI
- **Jinja2**: Template engine for HTML rendering
- **WebSockets**: Real-time communication for workout progress

### Frontend
- **HTML/CSS**: Basic UI structure and styling
- **JavaScript**: Client-side interactivity
- **Jinja2 Templates**: Server-rendered views

### Database
- **SQLAlchemy ORM**: Database abstraction layer
- **Support for multiple backends**: SQLite, PostgreSQL, MySQL
- **Database configuration**: Via secrets.yaml file

### External Integrations
- **Text-to-Speech**: Platform-specific implementations (macOS 'say' command)
- **Spotify**: Music control via AppleScript (macOS only)

## Development Environment

### Dependencies
- **Core Dependencies**:
  - pyyaml: Configuration and secrets management
  - SQLAlchemy: Database ORM
  - FastAPI: Web framework
  - Uvicorn: ASGI server
  - Jinja2: Template engine
  - python-multipart: Form data handling
  - websockets: WebSocket support
  - textual: Terminal UI components
  - psycopg2: PostgreSQL adapter

- **Platform-Specific Dependencies**:
  - dbus-python: Linux-specific (optional)
  - mysqlclient: MySQL support (optional)
  - psycopg2: PostgreSQL support

### System Requirements
- **Required System Packages**:
  - libdbus-1-dev: For D-Bus integration
  - libdbus-glib-1-dev: For D-Bus integration
  - festival: Text-to-speech engine
  - libssl-dev: SSL support

### Setup Process
1. Install system dependencies
2. Create and activate Python virtual environment
3. Install Python dependencies
4. Configure database connection in secrets.yaml
5. Initialize database tables
6. Bootstrap exercises (optional)

## Technical Constraints

### Platform Compatibility
- **Speech Engine**: Currently optimized for macOS, with limited support for other platforms
- **Music Integration**: Currently Spotify-only and macOS-only via AppleScript

### Database Configuration
- Requires proper database connection string in secrets.yaml
- Supports both production and QA database configurations

### Exercise Data
- Exercises can be loaded from JSON or database
- Exercise categories must match predefined enum values
- Exercise times are calculated based on default_time, repetition, and sides

## Tool Usage Patterns

### Database Initialization
```bash
python -m nerdouts.init_db [-f] [-e exercises.json] [-d] [-s]
```
- `-f`: Force recreation of tables
- `-e`: Path to exercises JSON file
- `-d`: Use QA database
- `-s`: Load static workouts from code

### Web Server
```bash
python -m nerdouts.web [-d]
```
- `-d`: Debug mode

### Configuration
- **config.json**: Default category weights and whitelist
- **secrets.yaml**: Database connection strings

## Development Patterns

### Code Organization
- **Models**: SQLAlchemy models in models.py
- **Web Interface**: FastAPI app in web.py
- **Workout Generation**: Logic in generate_dynamic_workout.py and static_workouts.py
- **Speech & Music**: Platform-specific implementations in speech.py and music.py
- **Database**: Connection handling in database.py and init_db.py

### Error Handling
- Database errors are caught and logged
- Speech engine timeouts are handled gracefully
- WebSocket disconnections are managed properly

### Testing
- Basic test files for core functionality
- Test JSON data for exercises

## Deployment Considerations

### Current TODOs
- Docker containerization planned
- Fix for duplicate workouts in static workout generator
- Fix for workout database writing
- Countdown timer functionality needs repair
- Add ability for required/excluded exercises

### Future Enhancements
- Cross-platform speech support
- Additional music service integrations
- Improved error handling and recovery
