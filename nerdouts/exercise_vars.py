from functools import partial
from generate_static_workout import load_exercises_from_db
from models import Exercise

class Exercises2():
    def __init__(self) -> None:
        self.exercises = load_exercises_from_db()
        self.BUTT_KICKERS = self.get_by_name("Butt Kickers")
        self.CLAMSHELLS = self.get_by_name("Clamshells")
        self.HIGH_KICKS = self.get_by_name("High Kicks")
        self.WALL_CLAMSHELL = self.get_by_name("Wall clamshell")
        self.CURLS = self.get_by_name("Curls")
        self.CALF_STRETCH = self.get_by_name("Calf Stretch")
        self.CALF_LIFTS = self.get_by_name("Calf Lifts")
        self.COBRA_POSE = self.get_by_name("Cobra pose")
        self.JUMP_ROPE = self.get_by_name("Jump rope")
        self.BIRD_BOPS = self.get_by_name("Bird bops")
        self.NORMAL_PUSHUPS = self.get_by_name("20 normal Pushups")
        self.BUTTERFLY_STRETCH = self.get_by_name("Butterfly Stretch")
        self.BRIDGE = self.get_by_name("Bridge")
        self.ONE_FOOT_BRIDGE = self.get_by_name("One foot bridge")
        self.DIAGONAL_BACKWARD_FONDAS = self.get_by_name("Diagonal backward fondas")
        self.SITUPS = self.get_by_name("Situps")
        self.INCLINE_PUSHUPS = self.get_by_name("20 incline Pushups")
        self.BAND_WALK = self.get_by_name("Band Walk")
        self.STRAIGHT_PLANK = self.get_by_name("Straight Plank")
        self.SIDE_PLANK = self.get_by_name("Side Plank")
        self.LEG_CIRCLES = self.get_by_name("Leg circles")
        self.ROLLER_ON_THE_BACK = self.get_by_name("Roller on the back")
        self.LEGS_CROSSED_STRETCH = self.get_by_name("Legs crossed stretch")
        self.NINJA_STRETCH = self.get_by_name("Ninja stretch")
        self.QUAD_STRETCH = self.get_by_name("Quad Stretch")
        self.NARROW_PUSHUPS = self.get_by_name("Narrow Pushups")
        self.BAND_SKATERS = self.get_by_name("Band Skaters")
        self.SKATER_JUMPS = self.get_by_name("Skater jumps")
        self.PULLUPS = self.get_by_name("Pullups")
        self.ROLLER_ON_THE_GROIN = self.get_by_name("Roller on the groin")
        self.LACROSSE_BALL_ON_THE_GROIN = self.get_by_name("Lacrosse Ball on the groin")
        self.HALF_ROLLER_SQUATS = self.get_by_name("Half Roller Squats")
        self.BACK_CURLS = self.get_by_name("Back curls")
        self.ROLLER_ON_THE_GLUTES = self.get_by_name("Roller on the glutes")
        self.WARRIOR = self.get_by_name("Warrior 2")
        self.HAMSTRING_STRETCH = self.get_by_name("Hamstring stretch")
        self.KNEE_TO_CHEST_STRETCH = self.get_by_name("Knee to chest stretch")
        self.SQUAT_HOLD = self.get_by_name("Squat hold")
        self.DIPS = self.get_by_name("Dips")
        self.BICYCLE_CRUNCHES = self.get_by_name("Bicycle crunches")
        self.MOUNTAIN_CLIMBERS = self.get_by_name("Mountain climbers")
        self.LUNGES = self.get_by_name("Lunges")
        self.HAND_ROLLER_ON_THE_GROIN = self.get_by_name("Hand roller on the groin")
        self.INNER_THIGH_ROLL = self.get_by_name("Inner thigh roll")
        self.LACROSSE_BALL_ON_HIP = self.get_by_name("Lacrosse ball on hip")
        self.HAMSTRING_ROLLER = self.get_by_name("Hamstring Roller")
        self.LACROSSE_BALL_ON_UPPER_KNEE = self.get_by_name("Lacrosse ball on upper knee")
        self.LACROSSE_BALL_BEHIND_KNEE = self.get_by_name("Lacrosse ball behind knee")
        self.ROLLER_ON_THE_QUAD = self.get_by_name("Roller on the quad")
        self.LACROSSE_BALL_ON_GLUTES = self.get_by_name("Lacrosse ball on glutes")
        self.CALF_ROLLER = self.get_by_name("Calf roller")
        self.GROIN_SQUEEZE = self.get_by_name("Groin Squeeze")
        self.HIP_MOBILITY = self.get_by_name("Hip mobility")
        self.GLUTE_RAISES = self.get_by_name("Glute raises")
        self.SUPINE_GLUTE_STRETCH = self.get_by_name("Supine glute stretch")
        self.LEGGED_SQUATS = self.get_by_name("1 legged squats")
        self.OTTOMAN_STEP_UPS = self.get_by_name("Ottoman step ups")
        self.DUMBBELL_BENCH_PRESS = self.get_by_name("Dumbbell bench press")
        self.DOWNWARD_DOG = self.get_by_name("Downward dog")
        self.UP_DOWNS = self.get_by_name("Up downs")
        self.LADDER = self.get_by_name("Ladder")
        self.JUMPING_JACKS = self.get_by_name("Jumping jacks")
        self.ROLLER_ON_THE_IT_BAND = self.get_by_name("Roller on the it band")
        self.SQUATS = self.get_by_name("Squats")
        self.SHADOW_BOXING = self.get_by_name("Shadow boxing")
        self.KICKSTAND_HIP_HINGE = self.get_by_name("Kickstand Hip Hinge")
        self.HIP_MOBILIZATION = self.get_by_name("Hip mobilization")
        self.ARM_SWINGS = self.get_by_name("Arm Swings")
        self.HALF_KNEELING_HIP_WEIGHTSHIFT = self.get_by_name("Half Kneeling Hip Weightshift")
        self.LATERAL_LUNGE = self.get_by_name("Lateral lunge")
        self.COPENHAGEN = self.get_by_name("Copenhagen")
        self.PLANK_WITH_LEG_LIFT = self.get_by_name("Plank with leg lift")
        self.HALF_KNEELING_HIP_FLEXOR_STRETCH = self.get_by_name("Half Kneeling Hip Flexor Stretch")
        self.QUADRAPED_ROCKBACK = self.get_by_name("Quadraped rockback")
        self.BRIDGE_ON_WALL = self.get_by_name("Bridge on wall")
        self.SPLIT_SQUAT = self.get_by_name("Split squat")
        self.STANDING_HIP_HINGE = self.get_by_name("Standing Hip Hinge")
        self.HIP_LIFT = self.get_by_name("Hip lift")
        self.HIP_ROCKBACK = self.get_by_name("Hip rockback")
        self.HAMSTRING_EXTENDER = self.get_by_name("Hamstring extender")
        self.DUMBBELL_ROWS = self.get_by_name("Dumbbell rows")
        self.BRIDGE_HAMSTRING_CURL = self.get_by_name("Bridge hamstring curl")
        self.POGO = self.get_by_name("POGO")
        self.SINGLE_LEG_BRIDGE = self.get_by_name("Single leg bridge")

    def get_by_name(self, name) -> Exercise:
        res = list(filter(lambda x: x.name == name, self.exercises))
        if len(res) > 1:
            raise Exception(f"Duplicate items with same name: {name} found")
        elif len(res) < 1:
            raise Exception(f"No exercise with name {name} found")
        else:
            return res[0]