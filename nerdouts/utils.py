from typing import List
from models import Exercise


def get_workout_length(exercises: List[Exercise]) -> int:
    return sum([exc.time for exc in exercises])
