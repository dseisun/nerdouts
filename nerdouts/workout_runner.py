from datetime import datetime
from typing import List, Optional, Protocol, Callable
import logging

from sqlalchemy.orm import Session

from config import Config, get_current_context
from generate_dynamic_workout import generate_dynamic_workout
from models import Exercise, Workout, WorkoutExercise
from music import MusicPlayer, SpotifyPlayer
from speech import countdown, get_speech_engine
from static_workouts import get_static_workouts
from exercise_vars import Exercises2
import utils

logger = logging.getLogger(__name__)

class WorkoutRunner:
    def __init__(
        self,
        music_player: Optional[MusicPlayer] = None,
        speech_engine: Optional[Callable[..., None]] = None
    ):
        self.music_player = music_player or SpotifyPlayer()
        self.speech_engine = speech_engine or get_speech_engine()

    def run_exercise(self, exercise: Exercise) -> bool:
        """Run a single exercise.
        
        Returns:
            bool: True if exercise was skipped, False otherwise
        """
        ctx = get_current_context()
        if ctx.debug:
            logger.info("QA MODE: Running exercise: %s", exercise.name)
            return False

        for _ in range(exercise.repetition):
            for side in exercise.sides:
                self.music_player.pause()
                self.speech_engine(exercise.sentence(side=side))
                self.music_player.play()
                
                if countdown(exercise.default_time):
                    logger.info("Exercise skipped by user")
                    return True
        return False

    def run_exercises(self, exercises: List[Exercise]) -> None:
        """Run a sequence of exercises."""
        workout_length = int(utils.get_workout_length(exercises) / 60)
        self.speech_engine(f'Workout should take: {workout_length} minutes')

        for exercise in exercises:
            skipped = self.run_exercise(exercise)
            if skipped:
                logger.info("Skipped exercise: %s", exercise.name)

        self.speech_engine('Workout finished. You\'re going to be so jacked')

class WorkoutService:
    def __init__(self, session: Session, runner: Optional[WorkoutRunner] = None):
        self.session = session
        self.runner = runner

    def run_dynamic_workout(self, total_time: int) -> List[Exercise]:
        """Run a dynamically generated workout.
        
        Returns:
            List[Exercise]: The list of exercises in the workout
        """
        exercises = Exercises2()
        config = Config(
            total_time=total_time,
            whitelist=[exercises.HIP_LIFT],
            blacklist=[exercises.CURLS]
        )
        workout = generate_dynamic_workout(config=config)
        exercise_list = [we.exercise for we in workout.workout_exercises]
        
        if self.runner:
            self.runner.run_exercises(exercise_list)
        
        self.session.add(workout)
        self.session.commit()
        
        return exercise_list

    def run_static_workout(self, workout_name: str) -> List[Exercise]:
        """Run a predefined static workout.
        
        Returns:
            List[Exercise]: The list of exercises in the workout
        """
        workouts = get_static_workouts()
        exercises = workouts[workout_name]
        self.session.add_all(exercises)

        workout = Workout()
        workout_exercises = [
            WorkoutExercise(
                workout=workout,
                exercise=exc,
                created_date=datetime.now(),
                time_per_set=exc.default_time,
                repetition=exc.repetition
            )
            for exc in exercises
        ]
        workout.workout_exercises = workout_exercises
        
        self.session.add_all(workout_exercises)
        
        if self.runner:
            self.runner.run_exercises(exercises)
            
        self.session.add(workout)
        self.session.commit()
        
        return exercises
