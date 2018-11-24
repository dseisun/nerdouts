import json
import models
import database
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Bootstrap exercises")
    parser.add_argument('-d', dest='debug', action='store_true', help='Bootstrap to the QA db')
    args = parser.parse_args()

    session = database.get_connection(args.debug)
    exercises = json.load(open('exercises.json', 'r'))

    for category in exercises['exercise_categories']:
        session.add(models.ExerciseCategory(**category))
    session.commit()

    for exercise in exercises['exercises']:
        session.add(models.Exercise(**exercise))
    session.commit()
