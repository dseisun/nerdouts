from typing import List
from nerdouts.models import Exercise


def get_workout_length(exercises: List[Exercise]) -> int:
    return sum([exc.time for exc in exercises])

# # A helper method that gives you a nicer interface to writing your static workout files. Realistically I want a UI for this
# def static_workout_generator(exercises_path=DEFAULT_EXERCISE_PATH) -> list[str]:
    
#     output = []
#     exercises = load_exercises_from_json(exercises_path)
#     mapped_exercises = dict(zip(range(len(exercises)), exercises))
#     for k,v in mapped_exercises.items():
#         print(f'{k}: {v.name}')
#     while True:
#         inp = input('Enger the number of the workout to add. Enter any char to finish:')
#         try:
#             i = int(inp)
#         except ValueError:
#             print(f'Didnt enter an int')
#             break
#         if inp == -1:
#             break
#         else:
#             output.append(f'get_by_name("{mapped_exercises[i].name}")')
#     return output
