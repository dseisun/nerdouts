import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from nerdouts.models import Base, Exercise, Workout, WorkoutExercise, ExerciseCategory
from nerdouts.generate_dynamic_workout import generate_dynamic_workout, generate_workout_exercises
from nerdouts.config import Config


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.fixture
def sample_exercises(in_memory_db):
    """Create sample exercises for testing"""
    exercises = [
        Exercise(
            name="Butt Kickers",
            category_id=ExerciseCategory.physical_therapy,
            side="Null",
            default_time=60,
            repetition=1,
            prompt="{name}",
            long_desc="Running in place while kicking your butt"
        ),
        Exercise(
            name="Clamshells",
            category_id=ExerciseCategory.physical_therapy,
            side="Both",
            default_time=30,
            repetition=2,
            prompt="10 {name}. {side} side. Keep the knee in line",
            long_desc="Lay on your side and with a band around your knees open and close your knees"
        ),
        Exercise(
            name="High Kicks",
            category_id=ExerciseCategory.stretch,
            side="Null",
            default_time=50,
            repetition=1,
            prompt="{name}",
            long_desc="Stand in place, and high kick to meet your opposite hand"
        ),
        Exercise(
            name="Curls",
            category_id=ExerciseCategory.strength,
            side="Null",
            default_time=60,
            repetition=3,
            prompt="{name}",
            long_desc="Normal bicep curls"
        ),
        Exercise(
            name="Foam Roll Calves",
            category_id=ExerciseCategory.rolling,
            side="Both",
            default_time=30,
            repetition=1,
            prompt="{name}",
            long_desc="Roll your calves"
        ),
        Exercise(
            name="Pushups",
            category_id=ExerciseCategory.strength,
            side="Null",
            default_time=45,
            repetition=2,
            prompt="{name}",
            long_desc="Standard pushups"
        )
    ]
    
    for exercise in exercises:
        in_memory_db.add(exercise)
    in_memory_db.commit()
    
    return exercises


@pytest.fixture
def basic_config(sample_exercises):
    """Create a basic config for testing"""
    return Config(
        total_time=10,  # 10 minutes
        whitelist=[],
        blacklist=[]
    )


class TestDynamicWorkoutGeneration:
    
    def test_basic_workout_generation(self, in_memory_db, sample_exercises, basic_config):
        """Test that a workout is generated with correct structure"""
        workout = generate_dynamic_workout(in_memory_db, basic_config)
        
        assert isinstance(workout, Workout)
        assert len(workout.workout_exercises) > 0
        assert all(isinstance(we, WorkoutExercise) for we in workout.workout_exercises)
    
    def test_respects_total_time_constraint(self, in_memory_db, sample_exercises, basic_config):
        """Test that generated workout doesn't exceed total time significantly"""
        workout = generate_dynamic_workout(in_memory_db, basic_config)
        
        total_time = workout.get_total_time
        expected_max_time = basic_config.total_time * 60  # Convert minutes to seconds
        
        # Allow some variance but shouldn't exceed by more than the longest exercise
        max_exercise_time = max(ex.time for ex in sample_exercises)
        assert total_time <= expected_max_time + max_exercise_time
    
    def test_respects_category_distribution(self, in_memory_db, sample_exercises, basic_config):
        """Test that exercises are distributed according to category weights"""
        workout = generate_dynamic_workout(in_memory_db, basic_config)
        
        # Group exercises by category
        category_times = {}
        for we in workout.workout_exercises:
            cat = we.exercise.category_id
            category_times[cat] = category_times.get(cat, 0) + we.exercise.time
        
        # Check that we have exercises from multiple categories
        assert len(category_times) >= 2
        
        # Verify no single category dominates completely (rough check)
        total_time = sum(category_times.values())
        if total_time > 0:
            for cat_time in category_times.values():
                assert cat_time / total_time <= 0.8  # No category should be more than 80%
    
    def test_whitelist_exercises_included(self, in_memory_db, sample_exercises):
        """Test that whitelisted exercises are always included"""
        whitelist_exercise = sample_exercises[0]  # Butt Kickers
        config = Config(
            total_time=10,
            whitelist=[whitelist_exercise],
            blacklist=[]
        )
        
        workout = generate_dynamic_workout(in_memory_db, config)
        
        # Check that whitelisted exercise is included
        workout_exercise_names = [we.exercise.name for we in workout.workout_exercises]
        assert whitelist_exercise.name in workout_exercise_names
    
    def test_blacklist_exercises_excluded(self, in_memory_db, sample_exercises):
        """Test that blacklisted exercises are never included"""
        blacklist_exercise = sample_exercises[1]  # Clamshells
        config = Config(
            total_time=10,
            whitelist=[],
            blacklist=[blacklist_exercise]
        )
        
        workout = generate_dynamic_workout(in_memory_db, config)
        
        # Check that blacklisted exercise is not included
        workout_exercise_names = [we.exercise.name for we in workout.workout_exercises]
        assert blacklist_exercise.name not in workout_exercise_names
    
    def test_custom_category_weights(self, in_memory_db, sample_exercises):
        """Test that custom category weights are respected"""
        # Create config with only strength exercises
        config = Config(
            total_time=5,
            categories={
                ExerciseCategory.physical_therapy: 0.0,
                ExerciseCategory.stretch: 0.0,
                ExerciseCategory.strength: 1.0,
                ExerciseCategory.rolling: 0.0
            }
        )
        
        workout = generate_dynamic_workout(in_memory_db, config)
        
        # All exercises should be strength exercises
        for we in workout.workout_exercises:
            if we.exercise not in config.whitelist:  # Exclude whitelisted exercises from this check
                assert we.exercise.category_id == ExerciseCategory.strength
    
    def test_exercise_properties_preserved(self, in_memory_db, sample_exercises, basic_config):
        """Test that exercise properties are correctly set in WorkoutExercise"""
        workout = generate_dynamic_workout(in_memory_db, basic_config)
        
        for we in workout.workout_exercises:
            assert we.time_per_set == we.exercise.default_time
            assert we.repetition == we.exercise.repetition
            assert isinstance(we.created_date, datetime)
            assert we.workout == workout
    
    def test_handles_insufficient_exercises(self, in_memory_db):
        """Test behavior when there aren't enough exercises to fill time"""
        # Create exercises for all categories but with short durations
        exercises = [
            Exercise(
                name="Quick PT",
                category_id=ExerciseCategory.physical_therapy,
                side="Null",
                default_time=5,
                repetition=1,
                prompt="{name}",
                long_desc="Quick PT exercise"
            ),
            Exercise(
                name="Quick Stretch",
                category_id=ExerciseCategory.stretch,
                side="Null",
                default_time=5,
                repetition=1,
                prompt="{name}",
                long_desc="Quick stretch"
            ),
            Exercise(
                name="Quick Strength",
                category_id=ExerciseCategory.strength,
                side="Null",
                default_time=5,
                repetition=1,
                prompt="{name}",
                long_desc="Quick strength"
            ),
            Exercise(
                name="Quick Rolling",
                category_id=ExerciseCategory.rolling,
                side="Null",
                default_time=5,
                repetition=1,
                prompt="{name}",
                long_desc="Quick rolling"
            )
        ]
        
        for exercise in exercises:
            in_memory_db.add(exercise)
        in_memory_db.commit()
        
        config = Config(total_time=10)  # 10 minutes, but only have 20 seconds total of exercise
        workout = generate_dynamic_workout(in_memory_db, config)
        
        # Should still generate a workout, even if short
        assert len(workout.workout_exercises) > 0
    
    def test_randomization_varies_workouts(self, in_memory_db, sample_exercises, basic_config):
        """Test that multiple workout generations produce different results"""
        workouts = []
        for _ in range(5):
            workout = generate_dynamic_workout(in_memory_db, basic_config)
            exercise_names = [we.exercise.name for we in workout.workout_exercises]
            workouts.append(tuple(exercise_names))  # Convert to tuple for comparison
        
        # At least some workouts should be different (allowing for small chance of duplicates)
        unique_workouts = set(workouts)
        assert len(unique_workouts) >= 2, "Workouts should vary due to randomization"
    
    def test_handles_missing_category_exercises(self, in_memory_db):
        """Test that workout generation handles when a category has no exercises"""
        # Only create exercises for some categories, not all
        exercises = [
            Exercise(
                name="Strength 1",
                category_id=ExerciseCategory.strength,
                side="Null",
                default_time=30,
                repetition=1,
                prompt="{name}",
                long_desc="Strength exercise"
            ),
            Exercise(
                name="Stretch 1",
                category_id=ExerciseCategory.stretch,
                side="Null",
                default_time=30,
                repetition=1,
                prompt="{name}",
                long_desc="Stretch exercise"
            )
            # Missing: physical_therapy and rolling exercises
        ]
        
        for exercise in exercises:
            in_memory_db.add(exercise)
        in_memory_db.commit()
        
        config = Config(total_time=5)
        
        # This should handle missing categories gracefully
        workout = generate_dynamic_workout(in_memory_db, config)
        
        # Should still generate a workout with available exercises
        assert len(workout.workout_exercises) > 0
        
        # Should only contain exercises from available categories
        workout_categories = {we.exercise.category_id for we in workout.workout_exercises}
        assert workout_categories.issubset({ExerciseCategory.strength, ExerciseCategory.stretch})
    
    def test_generate_workout_exercises_function(self, sample_exercises):
        """Test the generate_workout_exercises utility function"""
        workout = Workout()
        selected_exercises = sample_exercises[:3]
        
        workout_exercises = generate_workout_exercises(workout, selected_exercises)
        
        assert len(workout_exercises) == 3
        for we, orig_ex in zip(workout_exercises, selected_exercises):
            assert we.exercise == orig_ex
            assert we.workout == workout
            assert we.time_per_set == orig_ex.default_time
            assert we.repetition == orig_ex.repetition


class TestConfigValidation:
    
    def test_invalid_category_weights_sum(self):
        """Test that Config raises error when category weights don't sum to 1"""
        with pytest.raises(ValueError, match="Category weights must sum to 1"):
            Config(
                total_time=10,
                categories={
                    ExerciseCategory.physical_therapy: 0.5,
                    ExerciseCategory.stretch: 0.6,  # Sums to > 1
                    ExerciseCategory.strength: 0.0,
                    ExerciseCategory.rolling: 0.0
                }
            )
    
    def test_valid_category_weights(self):
        """Test that Config accepts valid category weights"""
        config = Config(
            total_time=10,
            categories={
                ExerciseCategory.physical_therapy: 0.3,
                ExerciseCategory.stretch: 0.3,
                ExerciseCategory.strength: 0.2,
                ExerciseCategory.rolling: 0.2
            }
        )
        
        assert config.total_time == 10
        assert abs(sum(config.categories.values()) - 1.0) < 0.001
    
    def test_exercise_category_times_calculation(self):
        """Test that exercise category times are calculated correctly"""
        config = Config(
            total_time=10,  # 10 minutes
            categories={
                ExerciseCategory.physical_therapy: 0.2,
                ExerciseCategory.stretch: 0.3,
                ExerciseCategory.strength: 0.3,
                ExerciseCategory.rolling: 0.2
            }
        )
        
        times = config.exercise_category_times
        
        # 10 minutes * 60 seconds = 600 seconds total
        assert times[ExerciseCategory.physical_therapy] == 120  # 20% of 600
        assert times[ExerciseCategory.stretch] == 180  # 30% of 600
        assert times[ExerciseCategory.strength] == 180  # 30% of 600
        assert times[ExerciseCategory.rolling] == 120  # 20% of 600