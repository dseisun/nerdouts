from fastapi import FastAPI, Request, Form, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uvicorn
import signal
import sys
import threading
import json
from typing import Optional, Dict

from static_workouts import get_static_workouts
from config import app_context, get_current_context
from sqlalchemy.orm import Session
from workout_runner import WorkoutService, WorkoutRunner
from speech import _stop_input, get_speech_engine
from music import SpotifyPlayer

app = FastAPI()

# Global workout runner for cleanup
active_workout_runner: Optional[WorkoutRunner] = None
workout_lock = threading.Lock()

# Active WebSocket connections
active_connections: Dict[int, WebSocket] = {}

# Set up templates directory
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Set up static files directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

def cleanup_workout():
    """Clean up any active workout session."""
    global active_workout_runner
    with workout_lock:
        if active_workout_runner:
            # Signal the input thread to stop
            _stop_input.set()
            # Clean up music player if needed
            if active_workout_runner.music_player:
                active_workout_runner.music_player.pause()
            active_workout_runner = None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Store connection
    connection_id = id(websocket)
    active_connections[connection_id] = websocket
    
    try:
        # Initialize workout components
        speech_engine = get_speech_engine()
        music_player = SpotifyPlayer()
        
        while True:
            data = await websocket.receive_json()
            command = data.get("command")
            
            if command == "start_exercise":
                # Get exercise details
                exercise = data.get("exercise", {})
                exercise_name = exercise.get("name", "")
                prompt = exercise.get("prompt", "")
                side = exercise.get("side")
                
                # Announce exercise
                music_player.pause()
                # Only include side in announcement if it exists
                announcement = prompt.format(name=exercise_name, side=side) if side else prompt.format(name=exercise_name)
                speech_engine(announcement)
                music_player.play()
                
                # Send confirmation back to frontend
                await websocket.send_json({"status": "exercise_started"})
                
            elif command == "complete_exercise":
                # Optional exercise completion announcement
                pass
                
            elif command == "finish_workout":
                music_player.pause()
                speech_engine("Workout finished. You're going to be so jacked")
                break
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Clean up connection
        if connection_id in active_connections:
            del active_connections[connection_id]
        
        # Clean up music player
        if music_player:
            music_player.pause()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with workout type selection."""
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )

@app.get("/workout/static", response_class=HTMLResponse)
async def static_workout_form(request: Request):
    """Form for selecting a static workout."""
    with app_context(debug=False):
        workouts = get_static_workouts()
        return templates.TemplateResponse(
            "static_workout.html",
            {
                "request": request,
                "workouts": workouts.keys()
            }
        )

@app.post("/workout/static/start", response_class=HTMLResponse)
async def start_static_workout(
    request: Request,
    workout_name: str = Form(...)
):
    """Start a static workout session."""
    with app_context(debug=False):
        with Session(get_current_context().engine) as session:
            service = WorkoutService(session)
            # Get workout exercises without running them
            exercises = get_static_workouts()[workout_name]
            # Save to database
            workout = service.run_static_workout(workout_name)
            
    return templates.TemplateResponse(
        "workout.html",
        {
            "request": request,
            "workout": [
                {
                    "name": e.name,
                    "default_time": e.default_time,
                    "repetition": e.repetition,
                    "sides": e.sides,
                    "prompt": e.prompt,
                    "side": e.side
                }
                for e in exercises
            ]
        }
    )

@app.get("/workout/dynamic", response_class=HTMLResponse)
async def dynamic_workout_form(request: Request):
    """Form for configuring a dynamic workout."""
    return templates.TemplateResponse(
        "dynamic_workout.html",
        {"request": request}
    )

@app.post("/workout/dynamic/start", response_class=HTMLResponse)
async def start_dynamic_workout(
    request: Request,
    time: int = Form(...)
):
    """Start a dynamic workout session."""
    with app_context(debug=False):
        with Session(get_current_context().engine) as session:
            service = WorkoutService(session)
            # Get workout exercises without running them
            workout = service.run_dynamic_workout(time)
            
    return templates.TemplateResponse(
        "workout.html",
        {
            "request": request,
            "workout": [
                {
                    "name": e.name,
                    "default_time": e.default_time,
                    "repetition": e.repetition,
                    "sides": e.sides,
                    "prompt": e.prompt,
                    "side": e.side
                }
                for e in workout
            ]
        }
    )

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    print("\nShutting down gracefully...")
    cleanup_workout()
    sys.exit(0)

def main():
    """Run the web server."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configure uvicorn with proper signal handling
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        reload=False,  # Disable auto-reload to ensure proper signal handling
    )
    server = uvicorn.Server(config)
    
    try:
        server.run()
    finally:
        cleanup_workout()

if __name__ == "__main__":
    main()
