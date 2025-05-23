import glob
from fastapi import FastAPI, Request, Form, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from textual import work
import uvicorn
import signal
import sys
import threading
import json
from typing import Optional, Dict, List
from pydantic import BaseModel
import argparse

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from nerdouts.static_workouts import get_static_workouts
from nerdouts.workout_runner import WorkoutService
from nerdouts.config import app_context, get_current_context, Config
from nerdouts.speech import _stop_input, get_speech_engine
from nerdouts.music import SpotifyPlayer
from nerdouts.models import Exercise, ExerciseCategory, Workout, WorkoutExercise, StaticWorkout


#TODO Add ability to add required/excluded exercises
#TODO Use docker for it


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
                announcement: str = prompt.format(name=exercise_name, side=side) if side else prompt.format(name=exercise_name)
                speech_engine(announcement)
                music_player.play()
                
                # Send confirmation back to frontend
                await websocket.send_json({"status": "exercise_started"})
                
            elif command == "complete_exercise":
                # Optional exercise completion announcement
                pass

            elif command == "ten_seconds_left":
                speech_engine("Ten seconds left")
                
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

class StaticWorkoutCreate(BaseModel):
    workout_name: str
    exercises: List[str]

@app.get("/workout/create-static", response_class=HTMLResponse)
async def create_static_workout_form(request: Request):
    """Form for creating a new static workout."""
    with Session(get_current_context().engine) as session:
        exercises = session.query(Exercise).all()
        exercise_list = [{
            "name": e.name,
            "time": e.time  # This includes repetitions and sides
        } for e in exercises]
        
    return templates.TemplateResponse(
        "create_static_workout.html",
        {
            "request": request,
            "exercises": exercise_list,
            "mode": "create"
        }
    )

@app.get("/workout/edit-static/{workout_name}", response_class=HTMLResponse)
async def edit_static_workout_form(request: Request, workout_name: str):
    """Form for editing an existing static workout."""
    # Only allow editing database workouts
    if not workout_name.startswith("db:"):
        raise HTTPException(status_code=403, detail="Cannot edit code-defined workouts")
    
    # Remove the "db:" prefix for the API call
    clean_workout_name = workout_name[3:]
    
    with Session(get_current_context().engine) as session:
        # Get all exercises for the dropdown
        exercises = session.query(Exercise).all()
        exercise_list = [{
            "name": e.name,
            "time": e.time
        } for e in exercises]
        
        # Get the existing workout data
        static_workouts = session.query(StaticWorkout).filter(
            StaticWorkout.workout_name == clean_workout_name
        ).order_by(StaticWorkout.id).all()
        
        if not static_workouts:
            raise HTTPException(status_code=404, detail="Workout not found")
        
        selected_exercises = [{
            "name": sw.exercise_name,
            "time": sw.exercise.time
        } for sw in static_workouts]
        
    return templates.TemplateResponse(
        "create_static_workout.html",
        {
            "request": request,
            "exercises": exercise_list,
            "mode": "edit",
            "workout_name": clean_workout_name,
            "selected_exercises": selected_exercises
        }
    )

@app.post("/api/static-workout/save")
async def save_static_workout(workout: StaticWorkoutCreate):
    """Save a new static workout."""
    if not workout.exercises:
        raise HTTPException(status_code=400, detail="Workout must contain at least one exercise")
    
    with Session(get_current_context().engine) as session:
        # Verify all exercises exist
        for exercise_name in workout.exercises:
            exercise = session.query(Exercise).filter(Exercise.name == exercise_name).first()
            if not exercise:
                raise HTTPException(status_code=400, detail=f"Exercise '{exercise_name}' not found")
        
        # Create StaticWorkout records for each exercise (allows duplicates)
        for exercise_name in workout.exercises:
            static_workout = StaticWorkout(
                workout_name=workout.workout_name,
                exercise_name=exercise_name
            )
            session.add(static_workout)
        try:
            session.commit()
            return {"message": "Workout saved successfully"}
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error saving workout")

@app.get("/api/static-workout/{workout_name}")
async def get_static_workout(workout_name: str):
    """Get a static workout for editing."""
    with Session(get_current_context().engine) as session:
        static_workouts = session.query(StaticWorkout).filter(
            StaticWorkout.workout_name == workout_name
        ).order_by(StaticWorkout.id).all()
        
        if not static_workouts:
            raise HTTPException(status_code=404, detail="Workout not found")
            
        return {
            "workout_name": workout_name,
            "exercises": [sw.exercise_name for sw in static_workouts]
        }

@app.put("/api/static-workout/{workout_name}")
async def update_static_workout(workout_name: str, workout: StaticWorkoutCreate):
    """Update an existing static workout."""
    if not workout.exercises:
        raise HTTPException(status_code=400, detail="Workout must contain at least one exercise")
    
    with Session(get_current_context().engine) as session:
        # Verify all exercises exist
        for exercise_name in workout.exercises:
            exercise = session.query(Exercise).filter(Exercise.name == exercise_name).first()
            if not exercise:
                raise HTTPException(status_code=400, detail=f"Exercise '{exercise_name}' not found")
        
        # Check if workout exists
        existing = session.query(StaticWorkout).filter(
            StaticWorkout.workout_name == workout_name
        ).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Workout not found")
        
        # Delete all existing entries for this workout
        session.query(StaticWorkout).filter(
            StaticWorkout.workout_name == workout_name
        ).delete()
        
        # Create new entries in the specified order
        for exercise_name in workout.exercises:
            static_workout = StaticWorkout(
                workout_name=workout_name,
                exercise_name=exercise_name
            )
            session.add(static_workout)
        
        try:
            session.commit()
            return {"message": "Workout updated successfully"}
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error updating workout")

@app.delete("/api/static-workout/{workout_name}")
async def delete_static_workout(workout_name: str):
    """Delete a static workout."""
    with Session(get_current_context().engine) as session:
        # Check if workout exists
        existing = session.query(StaticWorkout).filter(
            StaticWorkout.workout_name == workout_name
        ).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Workout not found")
        
        # Delete all entries for this workout
        deleted_count = session.query(StaticWorkout).filter(
            StaticWorkout.workout_name == workout_name
        ).delete()
        
        session.commit()
        return {"message": "Workout deleted successfully", "deleted_exercises": deleted_count}

@app.get("/workout/static", response_class=HTMLResponse)
async def static_workout_form(request: Request):
    """Form for selecting a static workout."""
    workouts = get_static_workouts()
    # Create a dictionary of workout names and their lengths
    workout_info = {
        name: int(sum(e.time for e in exercises) / 60)  # Convert seconds to minutes
        for name, exercises in workouts.items()
    }
    
    # Separate database workouts (can be edited/deleted) from code workouts
    db_workouts = [name for name in workouts.keys() if name.startswith("db:")]
    code_workouts = [name for name in workouts.keys() if name.startswith("code:")]
    
    return templates.TemplateResponse(
        "static_workout.html",
        {
            "request": request,
            "workouts": workouts.keys(),
            "workout_lengths": workout_info,
            "db_workouts": db_workouts,
            "code_workouts": code_workouts,
            "can_create": True
        }
    )

@app.post("/workout/static/start", response_class=HTMLResponse)
async def start_static_workout(
    request: Request,
    workout_name: str = Form(...)
):

    # Get workout exercises without running them
    workouts = get_static_workouts()
    if workout_name not in workouts:
        raise HTTPException(status_code=404, detail=f"Workout '{workout_name}' not found")
    
    exercises = workouts[workout_name]
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
        for we in workout.workout_exercises:
            workout_data.append({
                "name": we.exercise.name,
                "default_time": we.exercise.default_time,
                "repetition": we.exercise.repetition,
                "sides": we.exercise.sides,
                "prompt": we.exercise.prompt,
                "side": we.exercise.side
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
