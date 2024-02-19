# TODO Extend workout generator to generate a pre-defined workout
    # TODO Support generating a static workout
        # TODO Decide whether your source of exercises is in the database or json file
            # Does each workout have the ability to define a source? E.g. one could be from the db, one from a file?
# TODO Write tests
# TODO Remove usage of global "player"
# TODO Try to implement spotify player
# TODO Learn about AppleScript - https://chat.openai.com/c/7df9f2e4-2f20-475b-8d4d-534a72301475


#!/usr/bin/env python
import argparse
from config import Config

from datetime import datetime
import time
from database import get_connection
import logging
from generate_dynamic_workout import GenerateDynamicWorkout

from speech import countdown, get_speech_engine
from music import ClementinePlayer

logging.basicConfig(level=logging.INFO)


def run_exercise(exercise):
    for i in range(exercise.repetition):
        for side in exercise.sides:
            player.pause()
            tts(exercise.sentence(side=side))
            player.play()
            countdown(exercise.default_time)


def run_workout(workout, tts, debug=False):
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
    tts('Workout finished')

def parse_subargs():
    p2 = argparse.ArgumentParser(prog='Workout with static workouts')
    subparsers = p2.add_subparsers(help='this is a test', required=True, dest='cmd')
    dynamic = subparsers.add_parser('dynamic', help='test')
    dynamic.add_argument('-t', dest='time', type=int, help='Length (of time) of workout in minutes', required=True)
    dynamic.add_argument('-w', dest='workout', type=str, help='Workout config JSON', nargs='?', default='config.json')
    dynamic.add_argument('-d', dest='debug', action='store_true', help='Run in debug mode.')
    
    static = subparsers.add_parser('static', help='Run a predetermined workout. No config needed')
    static.add_argument('-w', dest='workout', type=str, help="The name of the workout as defined in static_workouts.py", required=True)
    static.add_argument('-d', dest='debug', action='store_true', help='Run in debug mode.')


    return p2.parse_args()

if __name__ == '__main__':
    
    args = parse_subargs()
    

    
    # ses = get_connection(args.debug)
    # config = Config(args.workout, args.time)
    # gw = WorkoutGenerator(ses)
    # wo = gw.generate_dynamic_workout(config)
    # global player
    # player = ClementinePlayer()
    # tts = get_speech_engine()
    # start = time.time()
    # run_workout(wo, tts=tts, debug=args.debug)
    # end = time.time()

    # ses.add(wo)
    # ses.commit()
    # logging.info('Workout took a total of: %.0f seconds', end-start)
