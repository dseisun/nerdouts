from typing import Dict, List, Set, Iterator
from sqlalchemy.orm import Session
from itertools import count, groupby
from random import random, sample

from models import Exercise, Workout, WorkoutExercise, ExerciseCategory
from config import Config, get_current_context
from datetime import datetime

def generate_dynamic_workout(session: Session, config: Config) -> Workout:
    # Convert whitelist Exercise objects to database Exercise objects
    whitelist_names = [exc.name for exc in config.whitelist]
    db_whitelist = session.query(Exercise).filter(Exercise.name.in_(whitelist_names)).all()
    
    # We start shifting the filter to be on name because ids might be different based on different dbs.
    # We want the key to be name and eventually to deprecate id
    exc_sorted_by_cat: list[Exercise] = sorted(session.query(Exercise).filter(Exercise.name.not_in(map(lambda x: x.name, config.blacklist))), key=lambda x: x.category_id)

    exc_by_cat_shuffled: Dict[ExerciseCategory, List[Exercise]] = {}
    for cat, exc_per_cat in groupby(exc_sorted_by_cat, lambda x: x.category_id):
        exc_by_cat_shuffled[cat] = sorted(list(exc_per_cat), key=lambda x: random())

    wo = Workout()

    exc_list: List[Exercise] = db_whitelist  # Use database whitelist exercises instead of config whitelist
    for category_name, category_time in config.exercise_category_times.items():
        cat_whitelisted_exercises: Iterator[Exercise] = filter(lambda exc: exc.category_id == category_name, db_whitelist)
        remaining_cat_time = category_time - sum(map(lambda exc: exc.time, cat_whitelisted_exercises))
        cat_excercises: List[Exercise] = exc_by_cat_shuffled[category_name]
        for i in count():
            exc = cat_excercises[i % len(cat_excercises)] # Loop around the list of exc if needed
            if remaining_cat_time > exc.time:
                exc_list.append(exc)
                remaining_cat_time -= exc.time
            else:
                break

    exc_list = sample(exc_list, len(exc_list)) # Shuffle workouts one more time
    for exc in exc_list:
        WorkoutExercise(
            workout=wo, 
            exercise=exc,
            created_date = datetime.now(),
            # TODO: Fix if we ever want to do dynamic time per set
            time_per_set = exc.default_time, 
            repetition = exc.repetition)
    return wo

def generate_workout_exercises(workout: Workout, exercises: List[Exercise]) -> List[WorkoutExercise]:
    return [
        WorkoutExercise(
            workout=workout, 
            exercise=exc,
            created_date = datetime.now(),
            # TODO: Fix if we ever want to do dynamic time per set
            time_per_set = exc.default_time, 
            repetition = exc.repetition)
        for exc in exercises]
        
    