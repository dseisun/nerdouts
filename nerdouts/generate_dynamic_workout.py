from typing import Dict, List, Set, Iterator
from sqlalchemy.orm import Session
from itertools import count, groupby
from random import random, sample

from models import Exercise, Workout, WorkoutExercise, ExerciseCategory
from config import Config


class GenerateDynamicWorkout:
    def __init__(self, session: Session) -> None:
        self.session: Session = session
        self.exercises: List[Exercise] = sorted(self.session.query(Exercise).all(), key=lambda x: x.category_id)
        # Map of category_id and shuffled Exercises
        self.shuffled_grouped_exercises: Dict[ExerciseCategory, List[Exercise]] = {
            cat: sorted(list(excs), key=lambda x: random())
            for cat, excs in groupby(self.exercises, lambda x: x.category_id)
        }

    def set_association(self, workout: Workout, exercises: List[Exercise]) -> List[WorkoutExercise]:
        return [WorkoutExercise(workout=workout, exercise=e) for e in exercises]

    def generate_dynamic_workout(self, config: Config) -> Workout:
        """Generate a workout based on the provided configuration.

        Args:
            config: Config object containing workout parameters

        Returns:
            A Workout object with associated exercises
        """
        wo = Workout()
        # Get whitelisted exercises
        exc_list: List[Exercise] = []
        whitelisted_exercises: List[Exercise] = (
            self.session.query(Exercise)
            .filter(Exercise.id.in_(config.whitelisted_exercises))
            .all()
        )
        blacklisted_exercises: List[Exercise] = (
            self.session.query(Exercise)
            .filter(Exercise.id.in_(config.blacklisted_exercises))
            .all()
        )
        # Add the whitelisted exercises first
        exc_list.extend(whitelisted_exercises)
        # Generate exercises per category time allotted excluding whitelisted exercises
        for cat_name, time in config.exercise_category_times.items():
            exc_for_cat = self.generate_exercises_for_category(
                cat_name,
                time,
                whitelisted_exercises,
                blacklisted_exercises
            )
            exc_list.extend(exc_for_cat)

        # Shuffle all the categories
        exc_list = sample(exc_list, len(exc_list))
        self.set_association(wo, exc_list)
        return wo

    def generate_exercises_for_category(
        self,
        category_name: ExerciseCategory,
        category_time: float,
        whitelisted_exercises: List[Exercise],
        blacklisted_exercises: List[Exercise]
    ) -> List[Exercise]:
        """Generate exercises for a specific category.

        We make sure exercises added aren't in the blacklist and remove the amount of time used
        from whitelisted exercises. We have this convoluted behavior so that even if the category
        isn't used according to the config (and this method isn't called) the whitelisted exercises
        make it in.

        Args:
            category_name: The category to generate exercises for
            category_time: Time allocated for this category in seconds
            whitelisted_exercises: List of exercises that must be included
            blacklisted_exercises: List of exercises that must be excluded

        Returns:
            List of exercises for the category
        """

        cat_whitelisted_exercises: Iterator[Exercise] = filter(
            lambda exc: exc.category_id == category_name,
            whitelisted_exercises
        )
        category_time = category_time - sum(map(lambda exc: exc.time, cat_whitelisted_exercises))
        exc_list: List[Exercise] = []
        cat_excercises: List[Exercise] = self.shuffled_grouped_exercises[category_name]
        blacklisted_ids: Set[int] = {exc.id for exc in blacklisted_exercises}

        for i in count():
            exc = cat_excercises[i % len(cat_excercises)]
            if category_time > exc.time:
                if exc.id not in blacklisted_ids:
                    exc_list.append(exc)
                    category_time -= exc.time
            else:
                break
        return exc_list
