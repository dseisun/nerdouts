#!/usr/bin/env python

import argparse
import logging
import time
from datetime import datetime
from typing import List, Optional, Protocol, Callable

from sqlalchemy.orm import Session

from config import Config, app_context, get_current_context
from generate_dynamic_workout import generate_dynamic_workout
from models import Exercise, Workout, WorkoutExercise
from music import MusicPlayer, SpotifyPlayer
from speech import countdown, get_speech_engine
from static_workouts import get_static_workouts
import utils

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
            time.sleep(0.5)
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
    def __init__(self, session: Session, runner: WorkoutRunner):
        self.session = session
        self.runner = runner

    def run_dynamic_workout(self, total_time: int) -> None:
        """Run a dynamically generated workout."""
        from exercise_vars import exercises
        config = Config(
            total_time=total_time,
            whitelist=[exercises.HIP_LIFT],
            blacklist=[exercises.CURLS]
        )
        workout = generate_dynamic_workout(config=config)
        self.runner.run_exercises([we.exercise for we in workout.workout_exercises])
        
        self.session.add(workout)
        self.session.commit()

    def run_static_workout(self, workout_name: str) -> None:
        """Run a predefined static workout."""
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
        self.runner.run_exercises(exercises)
        self.session.add(workout)
        self.session.commit()

from cli import parse_args

def main() -> None:
    args = parse_args()
    
    with app_context(debug=args.debug):
        runner = WorkoutRunner()
        
        with Session(get_current_context().engine) as session:
            service = WorkoutService(session, runner)
            
            if args.cmd == 'dynamic':
                service.run_dynamic_workout(args.time)
            elif args.cmd == 'static':
                service.run_static_workout(args.workout)

if __name__ == '__main__':
    main()
