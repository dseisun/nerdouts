from datetime import datetime
from typing import List, Optional, Protocol, Callable
import logging

from sqlalchemy.orm import Session

from nerdouts.config import Config, get_current_context
from nerdouts.generate_dynamic_workout import generate_dynamic_workout
from nerdouts.models import Exercise, Workout, WorkoutExercise
from nerdouts.music import MusicPlayer, SpotifyPlayer
from nerdouts.speech import countdown, get_speech_engine
from nerdouts.static_workouts import get_static_workouts
from nerdouts.exercise_vars import Exercises
import nerdouts.utils

logger = logging.getLogger(__name__)
class WorkoutService:
    def __init__(self, session: Session):
        self.session = session


    def run_dynamic_workout(self, total_time: int, config: Optional[Config] = None) -> Workout:
        """Run a dynamically generated workout. Returns the workout to be committed, 
        
        Args:
            total_time: Total workout time in minutes
            config: Optional Config object. If not provided, uses default configuration.
        
        Returns:
            List[Exercise]: The list of exercises in the workout
        """
        if config is None:
            exercises = Exercises()
            config = Config(
                total_time=total_time,
                whitelist=[exercises.HIP_LIFT],
                blacklist=[exercises.CURLS]
            )
        else:
            # Ensure total_time is set correctly in the provided config
            config.total_time = total_time
            
        workout = generate_dynamic_workout(self.session, config=config)
        exercise_list = [we.exercise for we in workout.workout_exercises]
        
        
        return workout

    