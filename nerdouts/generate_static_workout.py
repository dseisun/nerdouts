from models import Exercise, ExerciseCategory, Workout, WorkoutExercise


from itertools import count, groupby
from random import random, sample


class GenerateStaticWorkout:
    def __init__(self, session):
        self.session = session
        self.exercises = sorted(self.session.query(Exercise).all(), key=lambda x: x.category_id)
        # Map of category_id and Exercises
        self.shuffled_grouped_exercises = {cat: sorted(list(excs), key=lambda x: random())
                                           for cat, excs in
                                           groupby(self.exercises, lambda x: x.category_id)}

    def set_association(self, workout, exercises):
        return [WorkoutExercise(workout=workout, exercise=e) for e in exercises]

    def generate_dynamic_workout(self, config):
        """
        :param config: Config object
        :return: A list of WorkoutExercises
        """
        wo = Workout()
        # Get whitelisted exercises
        exc_list = []
        whitelisted_exercises = (self.session.query(Exercise)
                                 .filter(Exercise.id.in_(config.whitelisted_exercises)).all())
        blacklisted_exercises = (self.session.query(Exercise)
                                 .filter(Exercise.id.in_(config.blacklisted_exercises)).all())
        # Add the whitelisted exercises first
        exc_list.extend(whitelisted_exercises)
        # Generate exercises per category time allotted excluding whitelisted exercises
        for cat_name, time in config.exercise_category_times.items():
            exc_for_cat = self.generate_exercises_for_category(cat_name,
                                                               time,
                                                               whitelisted_exercises,
                                                               blacklisted_exercises)
            exc_list.extend(exc_for_cat)

        # Shuffle all the categories
        exc_list = sample(exc_list, len(exc_list))
        self.set_association(wo, exc_list)
        return wo

    def generate_exercises_for_category(self,
                                        category_name,
                                        category_time,
                                        whitelisted_exercises,
                                        blacklisted_exercises):
        """We make sure exercises added aren't in the blacklist and remove the amount of time used
        from whitelisted exercises. We have this convoluted behavior so that even if the category
        isn't used according to the config (and this method isn't called) the whitelisted exercises
        make it in"""
        cat = (self.session.query(ExerciseCategory)
               .filter(ExerciseCategory.name == category_name).first())

        cat_whitelisted_exercises = filter(lambda exc: exc.category_id == cat.id,
                                           whitelisted_exercises)
        category_time = category_time - sum(map(lambda exc: exc.time, cat_whitelisted_exercises))
        exc_list = []
        cat_excercises = self.shuffled_grouped_exercises[cat.id]
        for i in count():
            exc = cat_excercises[i % len(cat_excercises)]
            if category_time > exc.time:
                if exc.id not in set(map(lambda exc: exc.id, blacklisted_exercises)):
                    exc_list.append(exc)
                    category_time -= exc.time
            else:
                break
        return exc_list