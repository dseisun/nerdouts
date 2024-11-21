# TODO: Fixme for the new format
from typing import List
from itertools import count, groupby
from random import random, sample
import json
import os

from sqlalchemy.orm import Session
from config import get_current_context

from models import Exercise

DEFAULT_EXERCISE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'./exercises.json')

def load_exercises_from_db() -> List[Exercise]:
    """Load exercises from database using the current app context"""
    # This ensures we're using the correct database based on the app context
    ctx = get_current_context()
    with Session(ctx.engine) as session:
        return session.query(Exercise).all()

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
