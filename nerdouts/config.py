import logging
from .models import ExerciseCategory
from typing import Dict, List, Optional


class Config:
    """Configuration for workout generation, including category weights and time settings"""
    DEFAULT_CATEGORIES = {
        ExerciseCategory.physical_therapy: 0.20,
        ExerciseCategory.stretch: 0.25,
        ExerciseCategory.strength: 0.35,
        ExerciseCategory.rolling: 0.20
    }

    def __init__(
        self,
        total_time: int,
        categories: Optional[Dict[ExerciseCategory, float]] = None,
        whitelist: Optional[List[str]] = None,
        blacklist: Optional[List[str]] = None
    ):
        self.total_time = total_time
        self.categories = categories or self.DEFAULT_CATEGORIES.copy()
        self.whitelist: List[str] = whitelist or []
        self.blacklist: List[str] = blacklist or []

        # Validate weights sum to 1
        total_weight = sum(self.categories.values())
        if abs(total_weight - 1.0) > 0.001:  # Using small epsilon for float comparison
            raise ValueError(f"Category weights must sum to 1, got {total_weight}")

    @property
    def exercise_category_times(self) -> Dict[ExerciseCategory, float]:
        """Returns a map of category names to total times in seconds"""
        return {
            category: self.total_time * 60 * weight
            for category, weight in self.categories.items()
        }

    @property
    def whitelisted_exercises(self) -> List[str]:
        """Exercises that _have_ to be included in the workout.
        Expected behaviour is to add all the exercises even if it goes over time"""
        return self.whitelist

    @property
    def blacklisted_exercises(self) -> List[str]:
        """Exercises that _have_ to be excluded in the workout.
        This should return a list of exercises that can't be added.
        TODO: Currently input is just a list of id's from the config, but we can expand that to
        blacklisting categories and being more dynamic
        """
        return self.blacklist
