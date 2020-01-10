#!/usr/bin/env python
import argparse
from config import Config

from datetime import datetime
from models import Workout, Exercise, ExerciseCategory, WorkoutExercise
import time
from random import random, sample
from itertools import groupby, count
from database import get_connection
import logging

from coach import Coach
from music import ClementinePlayer

logging.basicConfig(level=logging.INFO)


class WorkoutGenerator(object):
    def __init__(self, session):
        self.session = session
        self.exercises = sorted(self.session.query(Exercise).all(), key=lambda x: x.category_id)
        # Map of category_id and Exercises
        self.shuffled_grouped_exercises = {cat: sorted(list(excs), key=lambda x: random())
                                           for cat, excs in
                                           groupby(self.exercises, lambda x: x.category_id)}

    def set_association(self, workout, exercises):
        return [WorkoutExercise(workout=workout, exercise=e) for e in exercises]

    def generate_workout(self, config):
        """
        :param config: Config object
        :return: A list of WorkoutExercises
        """
        wo = Workout()
        # Get whitelisted exercises
        exc_list = []
        whitelisted_exercises = (self.session.query(Exercise)
                                 .filter(Exercise.id.in_(config.whitelisted_exercises)).all())
        blacklisted_exercises = (self.session.query(Exercise)
                                 .filter(Exercise.id.in_(config.blacklisted_exercises)).all())
        # Add the whitelisted exercises first
        exc_list.extend(whitelisted_exercises)
        # Generate exercises per category time allotted excluding whitelisted exercises
        for cat_name, time in config.exercise_category_times.items():
            exc_for_cat = self.generate_exercises_for_category(cat_name,
                                                               time,
                                                               whitelisted_exercises,
                                                               blacklisted_exercises)
            exc_list.extend(exc_for_cat)

        # Shuffle all the categories
        exc_list = sample(exc_list, len(exc_list))
        self.set_association(wo, exc_list)
        return wo

    def generate_exercises_for_category(self,
                                        category_name,
                                        category_time,
                                        whitelisted_exercises,
                                        blacklisted_exercises):
        """We make sure exercises added aren't in the blacklist and remove the amount of time used
        from whitelisted exercises. We have this convoluted behavior so that even if the category
        isn't used according to the config (and this method isn't called) the whitelisted exercises
        make it in"""
        cat = (self.session.query(ExerciseCategory)
               .filter(ExerciseCategory.name == category_name).first())

        cat_whitelisted_exercises = filter(lambda exc: exc.category_id == cat.id,
                                           whitelisted_exercises)
        category_time = category_time - sum(map(lambda exc: exc.time, cat_whitelisted_exercises))
        exc_list = []
        cat_excercises = self.shuffled_grouped_exercises[cat.id]
        for i in count():
            exc = cat_excercises[i % len(cat_excercises)]
            if category_time > exc.time:
                if exc.id not in set(map(lambda exc: exc.id, blacklisted_exercises)):
                    exc_list.append(exc)
                    category_time -= exc.time
            else:
                break
        return exc_list


def countdown(exc_time):
    for sec in range(exc_time):
        logging.info("%d seconds until the next exercise" % (exc_time - sec))
        if exc_time - sec == 10:
            Coach.say("10 Seconds left")
        time.sleep(1)


def run_exercise(exercise):
    for i in range(exercise.repetition):
        for side in exercise.sides:
            player.pause()
            Coach.say(exercise.sentence(side=side))
            player.play()
            countdown(exercise.default_time)


def run_workout(workout, debug=False):
    player.next()
    for e in workout.workout_exercises:
        e.created_date = datetime.now()
        e.time_per_set = e.exercise.default_time
        e.repetition = e.exercise.repetition
        if not debug:
            run_exercise(e.exercise)
        else:
            logging.info("QA MODE: Running exercise: %s" % e.exercise)
            time.sleep(1)
    Coach.say('Workout finished')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Daniels workouts")
    parser.add_argument('-t', dest='time', type=int, help='Length (of time) of workout in minutes', required=True)
    parser.add_argument('-w', dest='workout', type=str, help='Workout config JSON', nargs='?', default='config.json')
    parser.add_argument('-d', dest='debug', action='store_true', help='Run in debug mode.')
    args = parser.parse_args()
    ses = get_connection(args.debug)
    config = Config(args.workout, args.time)
    gw = WorkoutGenerator(ses)
    wo = gw.generate_workout(config)
    global player
    player = ClementinePlayer()
    start = time.time()
    run_workout(wo, args.debug)
    end = time.time()

    ses.add(wo)
    ses.commit()
    logging.info('Workout took a total of: %.0f seconds', end-start)
