# Nerdouts

A fitness/workout management application that generates customizable workouts with voice guidance and music integration.

## Features

- **Dynamic Workouts**: Auto-generated based on time constraints and exercise category weights
- **Static Workouts**: Pre-defined routines stored in code or database
- **Exercise Management**: CRUD operations for exercises via web UI
- **Voice Guidance**: Text-to-speech announcements during workouts
- **Music Integration**: Spotify control (pause during announcements)
- **Web Interface**: FastAPI backend with HTML/JS frontend

## Quick Start

### Automated Setup (Recommended)

```bash
./scripts/dev_setup.sh
```

This will install dependencies, set up the database, and get you ready to develop.

### Manual Setup

1. **Install system dependencies** (Linux):
   ```bash
   sudo apt install libdbus-1-dev libdbus-glib-1-dev festival libssl-dev
   ```

2. **Install UV package manager**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install Python dependencies**:
   ```bash
   make dev-install
   ```

4. **Configure database**:
   ```bash
   cp nerdouts/secrets.yaml.template nerdouts/secrets.yaml
   # Edit secrets.yaml with your database credentials
   ```

5. **Initialize database**:
   ```bash
   make init-db-full
   ```

6. **Run the application**:
   ```bash
   make run
   ```

   Visit `http://localhost:8000` to use the web interface.

## Development

### Available Commands

See all available development commands:
```bash
make help
```

### Common Tasks

```bash
make run              # Start the web server
make test             # Run all tests
make test-cov         # Run tests with coverage report
make lint             # Run code linting
make format           # Auto-format code
make all-checks       # Run all quality checks
```

### Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines, testing, code quality
- **[CLAUDE.md](CLAUDE.md)** - Detailed project context, model mappings, architecture

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: SQLAlchemy ORM (PostgreSQL/MySQL/SQLite)
- **Frontend**: HTML templates with Jinja2, vanilla JavaScript
- **Real-time**: WebSockets for workout execution
- **Audio**: Client-side TTS via Web Speech API
- **Music**: Spotify Web SDK integration

## Configuration

Edit `config.json` to customize workout generation:
```json
{
  "categories": [
    {"name": "physical_therapy", "weight": 0.20},
    {"name": "stretch", "weight": 0.25},
    {"name": "strength", "weight": 0.35},
    {"name": "rolling", "weight": 0.20}
  ]
}
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

Creative Commons Attribution-Noncommercial-Share Alike license