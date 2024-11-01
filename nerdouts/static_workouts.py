from functools import partial
from typing import List
from generate_static_workout import get_exercise_by_name, load_exercises_from_json
from models import Exercise
get_by_name = partial(get_exercise_by_name, exercises=load_exercises_from_json())

workouts: dict[str, List[Exercise]] = {
    'sample': [
        get_by_name("Clamshells"),
        get_by_name("High Kicks"),
        get_by_name("Curls"),
        get_by_name("Calf Stretch"),
        get_by_name("Jump rope"),
        get_by_name("Narrow Pushups")
    ],
    'pt_cool_down_day': [
        get_by_name("Hip mobilization"),
        get_by_name('Half Kneeling Hip Flexor Stretch'),
        get_by_name('Quadraped rockback')
    ],
    'tmp': [
        get_by_name("Downward dog"),
        get_by_name("Hip mobilization"),
        get_by_name("Arm Swings"),
        get_by_name("Calf Lifts"),
        get_by_name('Half Kneeling Hip Flexor Stretch'),
        get_by_name("Dips"),
        get_by_name('Calf Stretch'),
        get_by_name('Quadraped rockback')
    ],

    'day_1': [
            get_by_name("Shadow boxing"),
            get_by_name("Hip rockback"),
            get_by_name("Hamstring extender"),
            get_by_name("Situps"),
            get_by_name("Downward dog"),
            get_by_name("Dips"),
            get_by_name("20 normal Pushups"),
            # get_by_name("Curls"),
            get_by_name("Arm Swings"),
            get_by_name("Straight Plank"),
            get_by_name("Calf Lifts"),
            get_by_name("Hip mobilization"),
            get_by_name("Jumping jacks"),
            # get_by_name("Half Kneeling Hip Flexor Stretch"),
            # get_by_name("Wall clamshell"),
            # get_by_name("Copenhagen"),
            # get_by_name("Plank with leg lift"),
            get_by_name("Calf Lifts"),
            # get_by_name("Split squat"),
            # get_by_name("Dumbbell bench press"),
            get_by_name("Situps"),
            # get_by_name("Lateral lunge"),
            # get_by_name("Squats"),
            get_by_name("Shadow boxing"),
            get_by_name("Downward dog"),
            # get_by_name("Downward dog"),
            # get_by_name("Jump rope")
    ],
    'day_2': [
        get_by_name("Dips"),
        get_by_name("Downward dog"),
        get_by_name("Shadow boxing"),
        get_by_name("Hip mobilization"),
        # get_by_name("Squats"),
        # get_by_name("Jumping jacks"),
        # get_by_name("Lateral lunge"),
        get_by_name("Roller on the quad"),
        get_by_name('Side Plank'),
        get_by_name("Situps"),
        get_by_name("Curls"),
        get_by_name("Dumbbell bench press"),
        get_by_name("20 normal Pushups"),
        get_by_name("Calf roller"),
        get_by_name("Arm Swings"),
        get_by_name("Calf Stretch")
    ],
    'nighttime': [
        get_by_name("Jumping jacks"),
        get_by_name("Dips"),
        get_by_name("Calf Lifts"),
        get_by_name("Curls"),
        get_by_name("Dumbbell bench press"),
        get_by_name("Downward dog"),
        get_by_name("Dips"),
        get_by_name("Curls"),
        get_by_name("Dumbbell bench press"),
    ],
    'no_cardio_pt': [
        get_by_name("Kickstand Hip Hinge"),
        get_by_name("Downward dog"),
        get_by_name("Hip mobilization"),
        get_by_name("Calf Lifts"),
        get_by_name("Copenhagen"),
        get_by_name("Plank with leg lift"),
        get_by_name("Downward dog"),
        get_by_name("Half Kneeling Hip Weightshift"),
        get_by_name("Curls"),
        get_by_name("Dumbbell bench press"),
        get_by_name("Situps"),
        get_by_name("Lateral lunge"),
        get_by_name("Squats"),
        get_by_name("Downward dog")
    ]
}