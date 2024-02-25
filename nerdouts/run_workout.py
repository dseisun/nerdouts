# TODO Extend workout generator to generate a pre-defined workout
    # TODO Support generating a static workout
        # TODO Decide whether your source of exercises is in the database or json file
            # Does each workout have the ability to define a source? E.g. one could be from the db, one from a file?
# TODO Write tests
# TODO Learn about AppleScript - https://chat.openai.com/c/7df9f2e4-2f20-475b-8d4d-534a72301475
# TODO Actually have static exercises write to a db
# TODO Support sqlite or other db types
# TODO show overall workout time to start
# TODO Decide to either use curses or website for display

#!/usr/bin/env python
import argparse
from typing import List
from config import Config
import utils
from datetime import datetime
import time
from database import get_connection
import logging
from generate_dynamic_workout import GenerateDynamicWorkout

from speech import countdown, get_speech_engine
import music

DEFAULT_MUSIC_PLAYER = music.SpotifyPlayer()

logging.basicConfig(level=logging.INFO)

# TODO: This relies on duck typing to work with StaticExercise and Exercise
def run_exercise(exercise, tts, player, debug=False):
    if not debug:
        for i in range(exercise.repetition):
            for side in exercise.sides:
                player.pause()
                tts(exercise.sentence(side=side))
                player.play()
                countdown(exercise.default_time)
    else:
        logging.info("QA MODE: Running exercise: %s" % exercise.name)
        time.sleep(1)

#TODO This needs to be fixed to work with the new argparse format. 
def run_dynamic_workout(workout, tts, debug=False):
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

#TODO: Implement
def run_static_workout(args: argparse.Namespace):
    from static_workouts import workouts
    tts = get_speech_engine()
    exercises = workouts[args.workout]
    
    tts('Workout should take: %s minutes' % int(utils.get_workout_length(exercises) / 60))
    for exc in exercises:
        run_exercise(exc, tts, DEFAULT_MUSIC_PLAYER, debug=args.debug)

    
def run_genstat(args: argparse.Namespace):
    from generate_static_workout import static_workout_generator
    output = static_workout_generator()
    for i in output:
        print(i)


def parse_args():
    parser = argparse.ArgumentParser(prog='Workout with static workouts')
    parser.add_argument('-d', dest='debug', action='store_true', help='Run in debug mode.')
    subparsers = parser.add_subparsers(help='this is a test', required=True, dest='cmd')

    dynamic = subparsers.add_parser('dynamic', help='test')
    dynamic.add_argument('-t', dest='time', type=int, help='Length (of time) of workout in minutes', required=True)
    dynamic.add_argument('-w', dest='workout', type=str, help='Workout config JSON', nargs='?', default='config.json')
    dynamic.set_defaults(func=run_dynamic_workout)

    static = subparsers.add_parser('static', help='Run a predetermined workout. No config needed')
    static.add_argument('-w', dest='workout', type=str, help="The name of the workout as defined in static_workouts.py", required=True)
    static.set_defaults(func=run_static_workout)

    genstat = subparsers.add_parser('genstat', help='Generate a static workout from a set of exercises')
    genstat.add_argument('-e', dest='exercise_file', type=str, help="The path of the json file containing the master list of workouts", required=True)
    genstat.set_defaults(func=run_genstat)
    return parser.parse_args()



if __name__ == '__main__':
    
    args: argparse.Namespace = parse_args()
    args.func(args)

    
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
