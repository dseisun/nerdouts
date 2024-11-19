import logging
from models import ExerciseCategory, Exercise
from typing import Dict, List, Optional
from database import set_engine_for_ctx
from contextlib import contextmanager

class AppContext:
    """Thread-safe application context for managing global state"""
    _context: Optional['AppContext'] = None

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.engine = set_engine_for_ctx(debug=debug)

        
        # Configure logging based on debug mode
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @classmethod
    def get_current(cls) -> 'AppContext':
        """Get the current application context"""
        if cls._context is None:
            raise RuntimeError("No application context available. Use 'with app_context(debug):'")
        return cls._context
    
    @classmethod
    def set_current(cls, context: Optional['AppContext']):
        """Set the current application context"""
        cls._context = context

@contextmanager
def app_context(debug: bool = False):
    """Context manager for application state"""
    previous_context = AppContext._context
    context = AppContext(debug=debug)
    AppContext.set_current(context)
    try:
        yield context
    finally:
        AppContext.set_current(previous_context)

def get_current_context() -> AppContext:
    """Helper function to get current application context"""
    return AppContext.get_current()

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
        whitelist: List[Exercise] = [],
        blacklist: List[Exercise] = []
    ):
        self.total_time = total_time
        self.categories = categories or self.DEFAULT_CATEGORIES.copy()
        self.whitelist = whitelist
        self.blacklist = blacklist

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
