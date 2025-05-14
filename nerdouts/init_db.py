from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from nerdouts.models import Base, Exercise, StaticWorkout
from nerdouts.static_workouts import get_static_workouts_from_code
from sqlalchemy import MetaData
import json
import argparse
import re
import os
from nerdouts.config import get_current_context, app_context

def name_to_var(name: str) -> str:
    name = re.sub(r'\d', '', name)
    return name.strip().replace(' ', '_').upper()

def generate_exercise_vars(exercises, output_file):
    with open(output_file, 'w') as outfile:
        outfile.write("""from functools import partial
from generate_static_workout import load_exercises_from_db
from models import Exercise

class Exercises():
    def __init__(self) -> None:
        self.exercises = load_exercises_from_db()
""")
        # Add each exercise as an instance attribute
        for exercise in exercises:
            var_name = name_to_var(exercise['name'])
            outfile.write(f"        self.{var_name} = self.get_by_name(\"{exercise['name']}\")\n")

        # Add the get_by_name method
        outfile.write("""
    def get_by_name(self, name) -> Exercise:
        res = list(filter(lambda x: x.name == name, self.exercises))
        if len(res) > 1:
            raise Exception(f"Duplicate items with same name: {name} found")
        elif len(res) < 1:
            raise Exception(f"No exercise with name {name} found")
        else:
            return res[0]
""")

def load_static_workouts(session):
    """Load static workouts from code into the database"""
    code_workouts = get_static_workouts_from_code()
    
    for workout_name, exercises in code_workouts.items():
        for exercise in exercises:
            static_workout = StaticWorkout(
                workout_name=workout_name,
                exercise_name=exercise.name
            )
            try:
                session.merge(static_workout)
            except IntegrityError:
                session.rollback()
                continue
    session.commit()

def load_exercises(exercise_path, debug, generate_vars=True):
    ctx = get_current_context()
    exercises = json.load(open(exercise_path))
    with Session(ctx.engine) as session:
        for e in exercises:
            exercise = Exercise(
                name=e['name'],
                category_id=e['category_id'],
                side=e['side'],
                default_time=e['default_time'],
                repetition=e['repetition'],
                prompt=e['prompt'],
                long_desc=e['long_desc']
            )
            try:
                session.merge(exercise)
            except IntegrityError:
                # If exercise already exists, rollback this one and continue with next
                session.rollback()
                continue
        # Commit all successful merges in a single transaction
        session.commit()
    
    if generate_vars:
        output_file = os.path.join(os.path.dirname(exercise_path), 'exercise_vars.py')
        generate_exercise_vars(exercises, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Prepare a database for storing workouts')
    parser.add_argument('-f', '--force', action='store_true' ,help='Drop and recreate existing tables if they exist')
    parser.add_argument('-e', '--exercises', help='Path to a JSON file of exercises for loading into the db')
    parser.add_argument('-d', dest='debug', action='store_true', help='Bootstrap to the QA db')

    parser.add_argument('-s', '--static-workouts', action='store_true', help='Load static workouts from code into the database')
    args: argparse.Namespace = parser.parse_args()
    
    with app_context(debug=args.debug) as ctx:
        engine = ctx.engine
        if args.force:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        
        with Session(engine) as session:
            if args.exercises:
                load_exercises(exercise_path=args.exercises, debug=args.debug, generate_vars=True)
            if args.static_workouts:
                load_static_workouts(session)
