#!/usr/bin/env python

# TODO Add git hook to generate static workouts on each commit
# TODO Support workout "Groups" - e.g. 3 sets of 3 different things where you do 1 set of each at a time
# TODO Add logging for total workout time to the end (somehow lost it)
# TODO Decide whether your source of exercises is in the database or json file
    # Does each workout have the ability to define a source? E.g. one could be from the db, one from a file?
# TODO Write tests
# TODO Actually have static exercises write to a db
# TODO Support sqlite or other db types
# TODO show overall workout time to start
# TODO Decide to either use curses or website for display - Website - Ncurses would be crazy
# TODO Add pydantic for validation?
import argparse
from typing import List, Union
from config import Config, app_context, get_current_context
from models import Exercise, Workout, WorkoutExercise
import utils
from datetime import datetime
import time
from sqlalchemy.orm import Session
import logging
from generate_dynamic_workout import generate_dynamic_workout, generate_workout_exercises
from speech import countdown, get_speech_engine
from static_workouts import get_static_workouts
import music

DEFAULT_MUSIC_PLAYER = music.SpotifyPlayer()

# TODO Support "pause" exercises. Exercises with a default time, but that 
# don't countdown and instead rely on user input to move forward 
# E.g. Jump rope or ladder exercise
def run_exercise(exercise, tts, player):
    ctx = get_current_context()
    if not ctx.debug:
        for i in range(exercise.repetition):
            for side in exercise.sides:
                player.pause()
                tts(exercise.sentence(side=side))
                player.play()
                if countdown(exercise.default_time):  # Check if exercise was skipped
                    logging.info("Exercise skipped by user")
                    return True  # Return True to indicate skip
    else:
        logging.info("QA MODE: Running exercise: %s" % exercise.name)
        time.sleep(.5)
    return False  # Return False to indicate normal completion

def run_exercises(exercises: list[Exercise]):
    tts = get_speech_engine()
    tts('Workout should take: %s minutes' % int(utils.get_workout_length(exercises) / 60))
    for exc in exercises:
        skipped = run_exercise(exc, tts, DEFAULT_MUSIC_PLAYER)
        if skipped:
            logging.info(f"Skipped exercise: {exc.name}")
    tts('Workout finished. You''re going to be so jacked')


# TODO: Fix to have a proper config interface
def run_dynamic_workout(args: argparse.Namespace):
    # Import exercises after app_context is established
    from exercise_vars import exercises
    wo = generate_dynamic_workout(config=Config(
        total_time=args.time,
        whitelist=[exercises.HIP_LIFT],
        blacklist=[exercises.CURLS]
    ))
    run_exercises([wo_exc.exercise for wo_exc in wo.workout_exercises])
    
    with Session(get_current_context().engine) as session:
        session.add(wo)
        session.commit()

def run_static_workout(args: argparse.Namespace):
    with Session(get_current_context().engine) as session:
        workouts = get_static_workouts()
        exercises = workouts[args.workout]
        session.add_all(exercises)
        wo = Workout()
        workout_exercises = [
            WorkoutExercise(
                workout=wo, 
                exercise=exc,
                created_date = datetime.now(),
                # TODO: Fix if we ever want to do dynamic time per set
                time_per_set = exc.default_time, 
                repetition = exc.repetition)
            for exc in exercises]
        # Explicitly set the workout_exercises relationship
        wo.workout_exercises = workout_exercises
        session.add_all(workout_exercises)
        run_exercises(exercises)
        session.add(wo)
        session.commit()

def parse_args():
    parser = argparse.ArgumentParser(prog='Workout with static workouts')
    parser.add_argument('-d', dest='debug', action='store_true', help='Run in debug mode.')
    subparsers = parser.add_subparsers(help='this is a test', required=True, dest='cmd')

    dynamic = subparsers.add_parser('dynamic', help='Generate a dynamic workout')
    dynamic.add_argument('-t', dest='time', type=int, help='Length (of time) of workout in minutes', required=True)
    dynamic.set_defaults(func=run_dynamic_workout)

    static = subparsers.add_parser('static', help='Run a predetermined workout. No config needed')
    static.add_argument('-w', dest='workout', type=str, help="The name of the workout as defined in static_workouts.py", required=True)
    static.set_defaults(func=run_static_workout)

    # genstat = subparsers.add_parser('genstat', help='Generate a static workout from a set of exercises')
    # genstat.add_argument('-e', dest='exercise_file', type=str, help="The path of the json file containing the master list of workouts", required=True)
    # genstat.set_defaults(func=run_genstat)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    with app_context(debug=args.debug):
        args.func(args)
