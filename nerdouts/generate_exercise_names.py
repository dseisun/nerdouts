# Generate python file to generate exercise variable names so I can use autocomplete when referencing exercises
import json
import re
import os

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),'./exercises.json')
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),'./exercise_vars.py')
exercises = json.load(open(INPUT_FILE))



def name_to_var(name: str) -> str:
    name = re.sub(r'\d', '', name)
    return name.strip().replace(' ', '_').upper()

with open(OUTPUT_FILE, 'w') as outfile:
    outfile.writelines("""from functools import partial
from generate_static_workout import get_exercise_by_name, load_exercises_from_json
get_by_name = partial(get_exercise_by_name, exercises=load_exercises_from_json())
""")
    for i in exercises:
        outfile.write("""{var_name} = get_by_name("{workout_name}")\n"""
                      .format(var_name=name_to_var(i['name']), workout_name=i['name']))
        


