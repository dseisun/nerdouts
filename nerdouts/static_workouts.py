from typing import List
from models import Exercise
from exercise_vars import Exercises

def get_static_workouts() -> dict[str, List[Exercise]]:
    exercises = Exercises()
    return {
        'sample': [
            exercises.CLAMSHELLS,
            exercises.HIGH_KICKS,
            exercises.CURLS,
            exercises.CALF_STRETCH,
            exercises.JUMP_ROPE,
            exercises.NARROW_PUSHUPS
        ],
        'pt_cool_down_day': [
            exercises.HIP_MOBILIZATION,
            exercises.HALF_KNEELING_HIP_FLEXOR_STRETCH,
            exercises.QUADRAPED_ROCKBACK
        ],
        'tmp': [
            exercises.DOWNWARD_DOG,
            exercises.HIP_MOBILIZATION,
            exercises.ARM_SWINGS,
            exercises.CALF_LIFTS,
            exercises.HALF_KNEELING_HIP_FLEXOR_STRETCH,
            exercises.DIPS,
            exercises.CALF_STRETCH,
            exercises.QUADRAPED_ROCKBACK
        ],
        'day_1': [
            exercises.SHADOW_BOXING,
            exercises.CURLS,
            exercises.HIP_ROCKBACK,
            exercises.HAMSTRING_EXTENDER,
            exercises.SITUPS,
            exercises.CURLS,
            exercises.DIPS,
            exercises.ARM_SWINGS,
            exercises.CALF_LIFTS,
            exercises.STRAIGHT_PLANK,
            exercises.DUMBBELL_ROWS,
            exercises.DUMBBELL_BENCH_PRESS,
            exercises.HIP_MOBILIZATION,
            exercises.JUMPING_JACKS,
            exercises.DUMBBELL_ROWS,
            exercises.DUMBBELL_BENCH_PRESS,
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
