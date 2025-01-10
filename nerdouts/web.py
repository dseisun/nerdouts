import glob
from fastapi import FastAPI, Request, Form, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from textual import work
import uvicorn
import signal
import sys
import threading
import json
from typing import Optional, Dict
import argparse

from static_workouts import get_static_workouts
from config import app_context, get_current_context, Config
from sqlalchemy.orm import Session
from workout_runner import WorkoutService
from speech import _stop_input, get_speech_engine
from music import SpotifyPlayer
from models import Exercise, ExerciseCategory, Workout, WorkoutExercise

#TODO When display falls asleep, timer seems to stop
#TODO 10 second countdown no longer works
#TODO Add ability to pause
#TODO Add ability to generate static workouts - migrate static workouts to db
#TODO Add ability to add required/excluded exercises
#TODO Write workout go database after (currently broken for dynamic and static)



app = FastAPI()

# Global workout runner for cleanup
workout_lock = threading.Lock()

# Active WebSocket connections and their exercises
active_connections: Dict[int, WebSocket] = {}
active_workout_exercises: Dict[int, list[Exercise]] = {}

# Set up templates directory
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Set up static files directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Store connection
    connection_id = id(websocket)
    active_connections[connection_id] = websocket
    
    # Get the exercises if they exist from the most recent request
    # This assumes the websocket connection is established right after the HTTP request
    request_ids = list(active_workout_exercises.keys())
    if request_ids:
        most_recent_request_id = request_ids[-1]
        active_workout_exercises[connection_id] = active_workout_exercises.pop(most_recent_request_id)
    
    music_player = None
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
                
                # Process completed exercises if they exist
                if connection_id in active_workout_exercises:
                    # Write WorkoutExercises and Workout to db

                    with Session(get_current_context().engine) as session:
                        completed_exercises = active_workout_exercises[connection_id]
                        workout_exercises = [
                            WorkoutExercise(
                                time_per_set = exercise.time,
                                repetition = exercise.repetition,
                                exercise = exercise
                            ) for exercise in completed_exercises]
                        workout = Workout()
                        workout.workout_exercises.extend(workout_exercises)
                        session.add(workout)
                        session.commit()
                        
                        print(f"finished workout and have these exercises: {completed_exercises}")
                    # Here you would typically write to database
                    # For now we just clean up
                    del active_workout_exercises[connection_id]
                
                break
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Clean up connection and exercises
        if connection_id in active_connections:
            del active_connections[connection_id]
        if connection_id in active_workout_exercises:
            del active_workout_exercises[connection_id]
            
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
    workouts = get_static_workouts()
    # Create a dictionary of workout names and their lengths
    workout_info = {
        name: int(sum(e.time for e in exercises) / 60)  # Convert seconds to minutes
        for name, exercises in workouts.items()
    }
    return templates.TemplateResponse(
        "static_workout.html",
        {
            "request": request,
            "workouts": workouts.keys(),
            "workout_lengths": workout_info
        }
    )

@app.post("/workout/static/start", response_class=HTMLResponse)
async def start_static_workout(
    request: Request,
    workout_name: str = Form(...)
):

    # Get workout exercises without running them
    exercises = get_static_workouts()[workout_name]
    workout = Workout()
    # Store exercises for later use - we'll use request id as temporary storage key
    request_id = id(request)
    active_workout_exercises[request_id] = exercises
            
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
    time: int = Form(...),
    weight_physical_therapy: float = Form(...),
    weight_stretch: float = Form(...),
    weight_strength: float = Form(...),
    weight_rolling: float = Form(...)
):
    """Start a dynamic workout session."""
    # Create custom category weights
    categories = {
        ExerciseCategory.physical_therapy: weight_physical_therapy,
        ExerciseCategory.stretch: weight_stretch,
        ExerciseCategory.strength: weight_strength,
        ExerciseCategory.rolling: weight_rolling
    }

    workout_data = []

    with Session(get_current_context().engine) as session:
        service = WorkoutService(session)
        # Create Config with custom category weights
        config = Config(total_time=time, categories=categories)
        # Get workout exercises and extract data while session is active
        workout = service.run_dynamic_workout(time, config=config)
        for e in workout:
            workout_data.append({
                "name": e.name,
                "default_time": e.default_time,
                "repetition": e.repetition,
                "sides": e.sides,
                "prompt": e.prompt,
                "side": e.side
            })
            
    return templates.TemplateResponse(
        "workout.html",
        {
            "request": request,
            "workout": workout_data
        }
    )

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    print("\nShutting down gracefully...")
    sys.exit(0)

def main():
    """Run the web server."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configure uvicorn with proper signal handling
    config = uvicorn.Config(
        app=app,
        host="localhost",
        port=8000,
        loop="asyncio",
        reload=False,  # Disable auto-reload to ensure proper signal handling
    )
    server = uvicorn.Server(config)
    
    try:
        server.run()
    finally:
        pass

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog='Webapp for workouts')
    parser.add_argument('--debug', '-d', action='store_true', default=False)
    args = parser.parse_args()
    with app_context(debug=args.debug):
        main()
