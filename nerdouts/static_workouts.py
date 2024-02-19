from functools import partial
from typing import List
from generate_static_workout import StaticExercise, get_exercise_by_name, load_exercises_from_json

get_by_name = partial(get_exercise_by_name, exercises=load_exercises_from_json())

workouts: dict[str, List[StaticExercise]] = {
    'workout': [
        get_by_name("Clamshells"),
        get_by_name("High Kicks"),
        get_by_name("Curls"),
        get_by_name("Calf Stretch"),
        get_by_name("Jump rope"),
        get_by_name("Narrow Pushups")
    ]
}