import json
import models
import database

session = database.Session()

exercises = json.load(open('exercises.json', 'r'))

for category in exercises['exercise_categories']:
    session.add(models.ExerciseCategory(**category))
session.commit()

for exercise in exercises['exercises']:
    session.add(models.Exercise(**exercise))

session.commit()
