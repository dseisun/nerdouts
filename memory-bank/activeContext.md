# Active Context: Nerdouts

## Current Focus
The Nerdouts project is a workout management system with a focus on providing guided workout experiences through voice prompts and music integration. The system supports both static (predefined) and dynamic (automatically generated) workouts, with exercises categorized into physical therapy, stretching, strength training, and rolling/recovery.

## Recent Changes
Based on the codebase examination, recent developments include:

1. **Web Interface Enhancements**:
   - Implementation of WebSocket communication for real-time workout progress
   - Creation of templates for workout selection and execution
   - Addition of static workout creation functionality

2. **Exercise Management**:
   - Expansion of exercise database with new exercises
   - Support for exercises with different sides (left/right)
   - Implementation of exercise categories and ordering

3. **Workout Generation**:
   - Implementation of dynamic workout generation based on time and category weights
   - Support for static workouts from both code and database
   - Merging of workouts from different sources with preference for database versions

## Next Steps
Based on TODOs in the code and the current state of the project:

1. **Bug Fixes**:
   - Fix issue with duplicate workouts in static workout generator
   - Repair 10-second countdown functionality
   - Fix workout database writing for both dynamic and static workouts

2. **Feature Enhancements**:
   - Add ability to specify required/excluded exercises in workouts
   - Implement Docker containerization for easier deployment
   - Improve cross-platform compatibility for speech and music integration

3. **Code Improvements**:
   - Refactor workout generation logic for better maintainability
   - Enhance error handling and recovery mechanisms
   - Improve test coverage for core functionality

## Active Decisions and Considerations

### Architecture Decisions
1. **Web-Based Interface**: The primary interface is web-based using FastAPI and Jinja2 templates, allowing for both desktop and mobile access.
2. **Real-Time Communication**: WebSockets are used for real-time workout progress and control, enabling a responsive user experience.
3. **Database Abstraction**: SQLAlchemy ORM provides flexibility for different database backends, with configuration via secrets.yaml.

### Implementation Patterns
1. **Exercise Categories**: Exercises are categorized into physical_therapy, stretch, strength, and rolling, with configurable weights for each category in dynamic workouts.
2. **Voice Guidance**: Text-to-speech integration provides hands-free workout guidance, with platform-specific implementations.
3. **Music Integration**: Spotify integration via AppleScript (macOS) enhances the workout experience with automatic pausing during announcements.

### Current Challenges
1. **Platform Compatibility**: Speech and music integration are currently optimized for macOS, limiting cross-platform usage.
2. **Database Writing**: Issues with writing completed workouts to the database need to be addressed.
3. **Static Workout Management**: Conflicts between code-defined and database-stored static workouts need resolution.

## Project Insights

### Key Learnings
1. **Exercise Categorization**: The four-category system (physical_therapy, stretch, strength, rolling) provides a balanced approach to workout composition.
2. **Voice Guidance**: Text-to-speech integration significantly enhances the workout experience by eliminating the need to look at screens.
3. **Workout Generation**: The dynamic workout generation algorithm effectively balances different exercise categories based on configurable weights.

### Important Patterns
1. **Context Manager Pattern**: The app_context manager ensures proper resource management and consistent application state.
2. **Factory Pattern**: Workout generation creates workouts based on configuration parameters.
3. **Repository Pattern**: Database access is abstracted through SQLAlchemy ORM.

### Critical Paths
1. **Exercise Flow**: From definition in JSON/database to execution with voice guidance.
2. **Workout Generation**: Selection of exercises based on category weights and time constraints.
3. **Real-Time Communication**: WebSocket-based progress tracking and control.
