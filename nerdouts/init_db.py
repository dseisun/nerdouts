from database import set_engine_for_ctx
from sqlalchemy.orm import Session

from models import Base, Exercise
from sqlalchemy import MetaData
import json
import argparse
from config import get_current_context, app_context

def load_exercises(exercise_path, debug):
    ctx = get_current_context()
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
    with Session(ctx.engine) as session:
        session.add_all(exercise_rows)  # Changed from exercises to exercise_rows
        session.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Prepare a database for storing workouts')
    parser.add_argument('-f', '--force', action='store_true' ,help='Drop and recreate existing tables if they exist')
    parser.add_argument('-e', '--exercises', help='Path to a JSON file of exercises for loading into the db')
    parser.add_argument('-d', dest='debug', action='store_true', help='Bootstrap to the QA db')

    args: argparse.Namespace = parser.parse_args()
    with app_context(debug=args.debug) as ctx:
        engine = ctx.engine
        if args.force:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        if args.exercises:
            load_exercises(exercise_path=args.exercises, debug=args.debug)
