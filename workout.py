#!/usr/bin/env python
import argparse
from datetime import datetime
import json
from models import Workout, Exercise, ExerciseCategory, WorkoutExercise
import time
from random import random, sample
from itertools import groupby, count
from database import Session
import logging

from coach import Coach
from music import Player

logging.basicConfig(level=logging.INFO)


class WorkoutGenerator(object):
    def __init__(self):
        self.session = Session()
        self.exercises = sorted(self.session.query(Exercise).all(), key=lambda x: x.category_id)
        self.shuffled_grouped_exercises = {cat: sorted(list(excs), key=lambda x: random())
                                           for cat, excs in
                                           groupby(self.exercises, lambda x: x.category_id)}
        self.wo = Workout()

    def set_association(self, exercises):
        return [WorkoutExercise(workout=self.wo, exercise=e) for e in exercises]

    def generate_workout(self, category_times):
        # Generate exercises per category time alotted
        exc_list = []
        for cat, time in category_times:
            exc_list.extend(self.generate_exercises_for_category(cat.id, time))

        # Shuffle all the categories
        exc_list = sample(exc_list, len(exc_list))

        self.set_association(exc_list)
        return self.wo

    def generate_exercises_for_category(self, category_id, category_time):
        exc_list = []
        cat_excercises = self.shuffled_grouped_exercises[category_id]
        for i in count():
            exc = cat_excercises[i % len(cat_excercises)]
            if category_time > exc.time:
                exc_list.append(exc)
                category_time -= exc.time
            else:
                break
        return exc_list


def config_to_category_times(session, config_path):
    with open(config_path) as data_file:
        workout_config = json.load(data_file)
    category_times = []
    for category in workout_config['categories']:
        exercise_category = session.query(ExerciseCategory).filter(ExerciseCategory.name == category['name']).first()
        time = args.time * 60 * category['weight']
        category_times.append((exercise_category, time))
    return category_times


def countdown(exc_time):
    for sec in range(exc_time):
        logging.info("%d seconds until the next exercise" % (exc_time - sec))
        if exc_time - sec == 10:
            Coach.say("10 Seconds left")
        time.sleep(1)


def run_exercise(exercise):
    for side in exercise.sides:
        for i in range(exercise.repetition):
            Player.pause()
            Coach.say(exercise.sentence(side=side))
            Player.play()
            countdown(exercise.default_time)


def run_workout(workout, debug=False):
    Player.next()
    for e in workout.workout_exercises:
        e.created_date = datetime.now()
        e.time_per_set = e.exercise.default_time
        e.repetition = e.exercise.repetition
        if not debug:
            run_exercise(e.exercise)
        else:
            logging.info("QA MODE: Running exercise: %s" % e)
            time.sleep(1)
    Coach.say('Workout finished')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Daniels workouts")
    parser.add_argument('-t', dest='time', type=int, help='Length (of time) of workout in minutes', required=True)
    parser.add_argument('-w', dest='workout', type=str, help='Workout config JSON', nargs='?', default='config.json')
    parser.add_argument('-d', dest='debug', action='store_true', help='Run in debug mode.')
    args = parser.parse_args()
    ses = Session()
    gw = WorkoutGenerator()
    category_times = config_to_category_times(ses, args.workout)
    wo = gw.generate_workout(category_times)

    run_workout(wo, args.debug)

    ses.add(wo)
    ses.commit()
