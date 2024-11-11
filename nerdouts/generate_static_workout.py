from typing import List
from itertools import count, groupby
from random import random, sample
import json
import os
from database import get_session
from models import Exercise

DEFAULT_EXERCISE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'./exercises.json')

def load_exercises_from_db() -> List[Exercise]:
    conn = get_session()
    return conn.query(Exercise).all()

def load_exercises_from_json(path=DEFAULT_EXERCISE_PATH) -> List[Exercise]:
    with open(path, 'r') as exc:
        payload = json.load(exc)
    exercises = []
    for exc in payload:
        exercises.append(
            Exercise(
                created_date=exc['date_added'],
                name=exc['name'],
                category_id=exc['category_id'],
                side=exc['side'],
                default_time=exc['default_time'],
                repetition=exc['repetition'],
                prompt=exc['prompt'],
                long_desc=exc['long_desc']
            )
        )
    return exercises



def get_exercise_by_name(name: str, exercises: List[Exercise]) -> Exercise:
    res = list(filter(lambda x: x.name == name, exercises))
    if len(res) > 1:
        raise Exception(f"Duplicate items with same name: {name} found")
    elif len(res) < 1:
        raise Exception(f"No exercise with name {name} found")
    else:
        return res[0]

# A helper method that gives you a nicer interface to writing your static workout files. Realistically I want a UI for this
def static_workout_generator(exercises_path=DEFAULT_EXERCISE_PATH) -> list[str]:
    
    output = []
    exercises = load_exercises_from_json(exercises_path)
    mapped_exercises = dict(zip(range(len(exercises)), exercises))
    for k,v in mapped_exercises.items():
        print(f'{k}: {v.name}')
    while True:
        inp = input('Enger the number of the workout to add. Enter any char to finish:')
        try:
            i = int(inp)
        except ValueError:
            print(f'Didnt enter an int')
            break
        if inp == -1:
            break
        else:
            output.append(f'get_by_name("{mapped_exercises[i].name}")')
    return output