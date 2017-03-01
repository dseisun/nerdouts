#!/usr/bin/env python

import argparse
import json
from models import Workout, Exercise, Session, Categories, WorkoutExercise
from random import random, shuffle, sample
import subprocess
from six import iteritems
from itertools import groupby, count


ses = Session()
# Todo: Move exercise and grouped exercise stuff to functions so they don't get executed before argparse
exercises = sorted(ses.query(Exercise).all(), key=lambda x: x.category.value)
grouped_exercises = {cat: sorted(list(excs), key=lambda x: random()) for cat, excs in groupby(exercises, lambda x: x.category.value)}


def generate_workout(time):
    wo = Workout()
    for e in sample(exercises, len(exercises)):
        wo.exercises.append(e)
        if wo.get_total_time > time:
            wo.exercises.pop()
            break
    return wo


def set_association(workout, exercises):
    return [WorkoutExercise(workout=workout, exercise=e) for e in exercises]


def generate_workout(category_times, shuffled=True):
    wo = Workout()
    exc_list = []
    for cat, time in category_times:
        for i in count():
            cat_excercises = grouped_exercises[cat]
            exc = cat_excercises[i%len(cat_excercises)]
            if time > exc.time:
                exc_list.append(exc)
                time -= exc.time
            else:
                break
    
    if shuffled:
        exc_list = sample(exc_list, len(exc_list))

    assoc = set_association(wo, exc_list)
    return wo

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Daniels workouts")
    parser.add_argument('-t', dest='time', type=int, help='Length (of time) of workout in minutes', required=True)
    parser.add_argument('-w', dest='workout', type=str, help='Workout config JSON', nargs='?', default='config.json')
    args = parser.parse_args()

    subprocess.call('clementine -l /home/dseisun/.config/Clementine/Playlists/Workout.xspf', shell=True)

    with open(args.workout) as data_file:
        workout_config = json.load(data_file)

    category_times = [(c['name'], args.time * 60 * c['weight']) for c in workout_config['categories']]
    wo = generate_workout(category_times)

    wo.iface.Next()
    wo.run_workout()
    ses.add(wo)
    ses.commit()
