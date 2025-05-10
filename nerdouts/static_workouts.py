from typing import List, Dict
from models import Exercise, StaticWorkout
from exercise_vars import Exercises
from sqlalchemy.orm import Session
from config import get_current_context
from itertools import groupby
from operator import attrgetter
import logging

def get_static_workouts_from_code() -> dict[str, List[Exercise]]:
    exercises = Exercises()
    workouts = {
        'sample': [
            exercises.CLAMSHELLS,
            exercises.HIGH_KICKS,
            exercises.CURLS,
            exercises.CALF_STRETCH,
            exercises.JUMP_ROPE,
            exercises.NARROW_PUSHUPS
        ],
        
        'groin_injured': [
            exercises.ARM_SWINGS,
            exercises.DOWNWARD_DOG,
            exercises.CURLS,
            exercises.DUMBBELL_ROWS,
            exercises.CALF_LIFTS,
            exercises.CALF_STRETCH,
            exercises.DUMBBELL_BENCH_PRESS,
            exercises.BACK_CURLS,
            exercises.QUAD_STRETCH,
            exercises.DIPS,
            exercises.SITUPS,
        ],
        'day_1': [
            exercises.SHADOW_BOXING,
            exercises.DOWNWARD_DOG,
            exercises.QUADRAPED_ROCKBACK,
            exercises.CURLS,
            exercises.DUMBBELL_ROWS,
            exercises.DUMBBELL_BENCH_PRESS,
            exercises.BACK_CURLS,
            exercises.SITUPS,
            exercises.CALF_LIFTS,
            exercises.CAPTAIN_MORGAN,
            exercises.DIPS,
            exercises.SHADOW_BOXING,
            exercises.KICKSTAND_HIP_HINGE,
            exercises.SQUATS,
            exercises.COPENHAGEN,
            exercises.HIP_MOBILIZATION,
            exercises.JUMPING_JACKS,
            exercises.CURLS,
            exercises.DUMBBELL_ROWS,
        ],
        'day_2': [
            exercises.DOWNWARD_DOG,
            exercises.ARM_SWINGS,
            exercises.ONE_FOOT_BRIDGE,
            exercises.BRIDGE_HAMSTRING_CURL,
            exercises.COPENHAGEN,
            exercises.POGO,
        ],
        'pre_bike': [
            exercises.SHADOW_BOXING,
            exercises.DOWNWARD_DOG,
            exercises.ARM_SWINGS,
            exercises.CURLS,
            exercises.DOWNWARD_DOG,
            exercises.BRIDGE_HAMSTRING_CURL,
            exercises.POGO,
            # exercises.SINGLE_LEG_BRIDGE,
            exercises.HIP_ROCKBACK,
        ],
        'nighttime': [
            exercises.JUMPING_JACKS,
            exercises.DIPS,
            exercises.CALF_LIFTS,
            exercises.CURLS,
            exercises.DUMBBELL_BENCH_PRESS,
            exercises.DOWNWARD_DOG,
            exercises.DIPS,
            exercises.CURLS,
            exercises.DUMBBELL_BENCH_PRESS,
        ],
        'post_work': [
            exercises.DOWNWARD_DOG,
            exercises.NINJA_STRETCH,
            exercises.HIP_MOBILITY,
            exercises.DOWNWARD_DOG,
            exercises.ROLLER_ON_THE_BACK,
            exercises.ROLLER_ON_THE_IT_BAND,
            exercises.DOWNWARD_DOG
        ],
        'no_cardio_pt': [
            exercises.KICKSTAND_HIP_HINGE,
            exercises.DOWNWARD_DOG,
            exercises.HIP_MOBILIZATION,
            exercises.CALF_LIFTS,
            exercises.COPENHAGEN,
            exercises.PLANK_WITH_LEG_LIFT,
            exercises.DOWNWARD_DOG,
            exercises.HALF_KNEELING_HIP_WEIGHTSHIFT,
            exercises.CURLS,
            exercises.DUMBBELL_BENCH_PRESS,
            exercises.SITUPS,
            exercises.LATERAL_LUNGE,
            exercises.SQUATS,
            exercises.DOWNWARD_DOG
        ],
        'no_equip': [
            exercises.SHADOW_BOXING,
            exercises.CURLS,
            exercises.DOWNWARD_DOG,
            exercises.SPLIT_SQUAT,
            exercises.NARROW_PUSHUPS,
            exercises.BUTT_KICKERS,
            exercises.INCLINE_PUSHUPS,
            exercises.DOWNWARD_DOG,
            # exercises.HIP_MOBILIZATION,
            exercises.CALF_LIFTS,
            exercises.CURLS,
            # exercises.PLANK_WITH_LEG_LIFT,
            exercises.SITUPS,
            exercises.SQUATS,
            exercises.DOWNWARD_DOG,
            exercises.DIPS,
            exercises.JUMPING_JACKS,
            exercises.SKATER_JUMPS
        ]
    }
    # Prepend 'code:' to all workout names
    return {f"code:{name}": exercises for name, exercises in workouts.items()}

def get_static_workouts_from_db() -> dict[str, List[Exercise]]:
    """Get static workouts from the database"""
    with Session(get_current_context().engine) as session:
        # Query all static workouts and eager load the related exercises
        static_workouts = session.query(StaticWorkout).join(StaticWorkout.exercise).all()
        
        # Group by workout_name and create a dictionary of workout name to list of exercises
        workouts = {}
        for workout_name, group in groupby(static_workouts, attrgetter('workout_name')):
            workouts[f"db:{workout_name}"] = [sw.exercise for sw in group]
        
        return workouts

def get_static_workouts() -> dict[str, List[Exercise]]:
    """Get static workouts from both code and database"""
    # Get workouts from both sources
    code_workouts = get_static_workouts_from_code()
    db_workouts = get_static_workouts_from_db()
    
    # Merge workouts, preferring database versions if there are duplicates
    merged_workouts = code_workouts.copy()
    merged_workouts.update(db_workouts)
    
    return merged_workouts
