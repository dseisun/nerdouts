from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
import logging

from models import Exercise, Workout, WorkoutExercise
from music_player import MusicPlayer
from speech import countdown, get_speech_engine
import utils

class ExerciseRunner:
    def __init__(self, tts, player: MusicPlayer, debug: bool = False):
        self.tts = tts
        self.player = player
        self.debug = debug

    def run_exercise(self, exercise: Exercise) -> bool:
        if not self.debug:
            for _ in range(exercise.repetition):
                for side in exercise.sides:
                    self.player.pause()
                    self.tts(exercise.sentence(side=side))
                    self.player.play()
                    if countdown(exercise.default_time):
                        logging.info("Exercise skipped by user")
                        return True
        else:
            logging.info(f"QA MODE: Running exercise: {exercise.name}")
        return False

class WorkoutRunner:
    def __init__(self, session: Session, player: MusicPlayer, debug: bool = False):
        self.session = session
        self.exercise_runner = ExerciseRunner(get_speech_engine(), player, debug)
    
    def run_exercises(self, exercises: List[Exercise]) -> None:
        total_time = int(utils.get_workout_length(exercises) / 60)
        self.exercise_runner.tts(f'Workout should take: {total_time} minutes')
        
        for exc in exercises:
            skipped = self.exercise_runner.run_exercise(exc)
            if skipped:
                logging.info(f"Skipped exercise: {exc.name}")
        
        self.exercise_runner.tts("Workout finished. You're going to be so jacked")

    def create_workout(self, exercises: List[Exercise]) -> Workout:
        wo = Workout()
        workout_exercises = [
            WorkoutExercise(
                workout=wo,
                exercise=exc,
                created_date=datetime.now(),
                time_per_set=exc.default_time,
                repetition=exc.repetition
            )
            for exc in exercises
        ]
        wo.workout_exercises = workout_exercises
        self.session.add_all(exercises)
        self.session.add_all(workout_exercises)
        self.session.add(wo)
        return wo