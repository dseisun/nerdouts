from database import get_engine, get_session
from models import Base, Exercise
from sqlalchemy import MetaData
import json
import argparse

def load_exercises(exercise_path):
    exercises = json.load(open(exercise_path))
    exercise_rows = []
    for e in exercises:
        exercise_rows.append(
            Exercise(name=e['name']
                ,category_id=e['category_id']
                ,side=e['side']
                ,default_time=e['default_time']
                ,repetition=e['repetition']
                ,prompt=e['prompt']
                ,long_desc=e['long_desc']))

    conn = get_session()
    conn.add_all(exercise_rows)  # Changed from exercises to exercise_rows
    conn.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Prepare a database for storing workouts')
    parser.add_argument('-f', '--force', action='store_true' ,help='Drop and recreate existing tables if they exist')
    parser.add_argument('-e', '--exercises', help='Path to a JSON file of exercises for loading into the db')
    parser.add_argument('-d', dest='debug', action='store_true', help='Bootstrap to the QA db')

    args: argparse.Namespace = parser.parse_args()
    engine = get_engine(args.debug)
    if args.force:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    if args.exercises:
        load_exercises(exercise_path=args.exercises)
