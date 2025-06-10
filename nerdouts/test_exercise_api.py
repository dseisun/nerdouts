import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from nerdouts.web import app
from nerdouts.models import Base, Exercise, ExerciseCategory, StaticWorkout
from nerdouts.config import app_context, get_current_context


@pytest.fixture
def test_db():
    """Create a test database that persists for the test session"""
    # Create an in-memory SQLite database with check_same_thread=False for FastAPI
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    
    # Create a sessionmaker
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Override the get_current_context to use our test engine
    with app_context(debug=True):
        get_current_context().engine = engine
        yield TestingSessionLocal()
    
    # Cleanup
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(test_db):
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def sample_exercise(test_db):
    """Create a sample exercise in the database"""
    exercise = Exercise(
        name="Test Push-ups",
        category_id=ExerciseCategory.strength,
        side="Null",
        default_time=45,
        repetition=3,
        prompt="{name}",
        long_desc="Standard push-ups for testing"
    )
    test_db.add(exercise)
    test_db.commit()
    test_db.refresh(exercise)
    return exercise


@pytest.fixture
def multiple_exercises(test_db):
    """Create multiple exercises for testing"""
    exercises = [
        Exercise(
            name="Test Squats",
            category_id=ExerciseCategory.strength,
            side="Null",
            default_time=60,
            repetition=2,
            prompt="{name}",
            long_desc="Bodyweight squats"
        ),
        Exercise(
            name="Test Lunges",
            category_id=ExerciseCategory.strength,
            side="Both",
            default_time=30,
            repetition=2,
            prompt="{name} - {side} side",
            long_desc="Forward lunges"
        ),
        Exercise(
            name="Test Hamstring Stretch",
            category_id=ExerciseCategory.stretch,
            side="Both",
            default_time=30,
            repetition=1,
            prompt="{name} - {side} side",
            long_desc="Seated hamstring stretch"
        ),
    ]
    for ex in exercises:
        test_db.add(ex)
    test_db.commit()
    return exercises


class TestExerciseAPI:
    """Test class for exercise API endpoints"""
    
    def test_get_exercises_empty(self, client):
        """Test getting exercises when database is empty"""
        response = client.get("/api/exercises")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_exercises_with_data(self, client, sample_exercise, multiple_exercises):
        """Test getting exercises when database has data"""
        response = client.get("/api/exercises")
        assert response.status_code == 200
        exercises = response.json()
        assert len(exercises) == 4  # 1 sample + 3 multiple
        
        # Check that all required fields are present
        for exercise in exercises:
            assert "id" in exercise
            assert "name" in exercise
            assert "category" in exercise
            assert "description" in exercise
            assert "time_per_set" in exercise
            assert "reps" in exercise
            assert "side" in exercise
            assert "prompt" in exercise
            assert "time" in exercise
    
    def test_create_exercise_minimal(self, client):
        """Test creating an exercise with minimal required fields"""
        exercise_data = {
            "name": "New Exercise",
            "category": "strength",
            "time_per_set": 30
        }
        response = client.post("/api/exercises", json=exercise_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Exercise"
        assert data["category"] == "strength"
        assert "id" in data
        assert data["message"] == "Exercise created successfully"
    
    def test_create_exercise_full(self, client):
        """Test creating an exercise with all fields"""
        exercise_data = {
            "name": "Full Exercise",
            "category": "physical_therapy",
            "description": "A complete exercise description",
            "time_per_set": 45,
            "reps": 3,
            "side": "Both",
            "prompt": "Do {name} on {side} side"
        }
        response = client.post("/api/exercises", json=exercise_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Full Exercise"
        assert data["category"] == "physical_therapy"
    
    def test_create_exercise_duplicate_name(self, client, sample_exercise):
        """Test creating an exercise with duplicate name"""
        exercise_data = {
            "name": "Test Push-ups",  # Same as sample_exercise
            "category": "strength",
            "time_per_set": 30
        }
        response = client.post("/api/exercises", json=exercise_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_create_exercise_invalid_category(self, client):
        """Test creating an exercise with invalid category"""
        exercise_data = {
            "name": "Invalid Category Exercise",
            "category": "invalid_category",
            "time_per_set": 30
        }
        response = client.post("/api/exercises", json=exercise_data)
        assert response.status_code == 400
        assert "Invalid category" in response.json()["detail"]
    
    def test_update_exercise(self, client, sample_exercise):
        """Test updating an existing exercise"""
        update_data = {
            "name": "Updated Push-ups",
            "category": "strength",
            "description": "Updated description",
            "time_per_set": 60,
            "reps": 4,
            "side": "Null",
            "prompt": "Updated {name}"
        }
        response = client.put(f"/api/exercises/{sample_exercise.id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Exercise updated successfully"
        
        # Verify the update
        response = client.get("/api/exercises")
        exercises = response.json()
        updated = next(e for e in exercises if e["id"] == sample_exercise.id)
        assert updated["name"] == "Updated Push-ups"
        assert updated["time_per_set"] == 60
        assert updated["reps"] == 4
    
    def test_update_exercise_not_found(self, client):
        """Test updating a non-existent exercise"""
        update_data = {
            "name": "Non-existent",
            "category": "strength",
            "time_per_set": 30
        }
        response = client.put("/api/exercises/9999", json=update_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_exercise_duplicate_name(self, client, sample_exercise, multiple_exercises):
        """Test updating an exercise to have a duplicate name"""
        update_data = {
            "name": "Test Squats",  # Name from multiple_exercises
            "category": "strength",
            "time_per_set": 30
        }
        response = client.put(f"/api/exercises/{sample_exercise.id}", json=update_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_delete_exercise(self, client, sample_exercise):
        """Test deleting an exercise"""
        response = client.delete(f"/api/exercises/{sample_exercise.id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Exercise deleted successfully"
        
        # Verify deletion
        response = client.get("/api/exercises")
        exercises = response.json()
        assert not any(e["id"] == sample_exercise.id for e in exercises)
    
    def test_delete_exercise_not_found(self, client):
        """Test deleting a non-existent exercise"""
        response = client.delete("/api/exercises/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_delete_exercise_used_in_workout(self, client, test_db, sample_exercise):
        """Test deleting an exercise that's used in a static workout"""
        # Create a static workout using the exercise
        static_workout = StaticWorkout(
            workout_name="Test Workout",
            exercise_name=sample_exercise.name
        )
        test_db.add(static_workout)
        test_db.commit()
        
        response = client.delete(f"/api/exercises/{sample_exercise.id}")
        assert response.status_code == 400
        assert "used in static workouts" in response.json()["detail"]
    
    def test_side_field_handling(self, client):
        """Test that side field correctly handles all four options"""
        side_options = ["Null", "Both", "Left", "Right"]
        
        for i, side in enumerate(side_options):
            exercise_data = {
                "name": f"Side Test {i}",
                "category": "stretch",
                "time_per_set": 30,
                "side": side
            }
            response = client.post("/api/exercises", json=exercise_data)
            assert response.status_code == 200
        
        # Test empty side defaults to "Null"
        exercise_data = {
            "name": "No Side Test",
            "category": "stretch",
            "time_per_set": 30
        }
        response = client.post("/api/exercises", json=exercise_data)
        assert response.status_code == 200
        
        # Verify all were created correctly
        response = client.get("/api/exercises")
        exercises = response.json()
        created_exercises = [e for e in exercises if "Side Test" in e["name"] or e["name"] == "No Side Test"]
        assert len(created_exercises) == 5
        
        # Check side values
        side_values = [e["side"] for e in created_exercises]
        assert "Null" in side_values
        assert "Both" in side_values
        assert "Left" in side_values
        assert "Right" in side_values


class TestExercisePages:
    """Test class for exercise management page routes"""
    
    def test_exercises_page(self, client):
        """Test the main exercises management page"""
        response = client.get("/exercises")
        assert response.status_code == 200
        assert b"Manage Exercises" in response.content
        assert b"Add New Exercise" in response.content
    
    def test_new_exercise_form(self, client):
        """Test the new exercise form page"""
        response = client.get("/exercises/new")
        assert response.status_code == 200
        assert b"New Exercise" in response.content
        assert b"Exercise Name" in response.content
    
    def test_edit_exercise_form(self, client, sample_exercise):
        """Test the edit exercise form page"""
        response = client.get(f"/exercises/edit/{sample_exercise.id}")
        assert response.status_code == 200
        assert b"Edit Exercise" in response.content
        assert b"Test Push-ups" in response.content
    
    def test_edit_exercise_form_not_found(self, client):
        """Test editing a non-existent exercise"""
        response = client.get("/exercises/edit/9999")
        assert response.status_code == 404