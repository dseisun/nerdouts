import json
import models


session = models.Session()

exercises = json.load(open('exercises.json', 'r'))
for exercise in exercises['exercises']:
    session.add(models.Exercise(**exercise))
session.commit()
