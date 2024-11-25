import argparse
from typing import Any, Callable

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='Workout with static workouts')
    parser.add_argument('-d', dest='debug', action='store_true', help='Run in debug mode.')
    subparsers = parser.add_subparsers(help='Workout type selection', required=True, dest='cmd')

    dynamic = subparsers.add_parser('dynamic', help='Generate a dynamic workout')
    dynamic.add_argument('-t', dest='time', type=int, help='Length (of time) of workout in minutes', required=True)

    static = subparsers.add_parser('static', help='Run a predetermined workout. No config needed')
    static.add_argument('-w', dest='workout', type=str, help="The name of the workout as defined in static_workouts.py", required=True)

    return parser

def parse_args() -> argparse.Namespace:
    parser = create_parser()
    return parser.parse_args()