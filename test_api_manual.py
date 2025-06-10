#!/usr/bin/env python3
"""
Manual API testing script for exercise management.
This script helps quickly test the exercise API endpoints during development.

Usage:
    python test_api_manual.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def pretty_print(response):
    """Pretty print JSON response"""
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 50)

def test_get_exercises():
    """Get all exercises"""
    print("\n=== GET ALL EXERCISES ===")
    response = requests.get(f"{BASE_URL}/api/exercises")
    pretty_print(response)
    return response.json() if response.status_code == 200 else []

def test_create_exercise(name, category="strength", **kwargs):
    """Create a new exercise"""
    print(f"\n=== CREATE EXERCISE: {name} ===")
    data = {
        "name": name,
        "category": category,
        "time_per_set": kwargs.get("time_per_set", 30),
        "description": kwargs.get("description", ""),
        "reps": kwargs.get("reps", 1),
        "side": kwargs.get("side", "Null"),
        "prompt": kwargs.get("prompt", "{name}")
    }
    response = requests.post(f"{BASE_URL}/api/exercises", json=data)
    pretty_print(response)
    return response.json() if response.status_code == 200 else None

def test_update_exercise(exercise_id, **updates):
    """Update an exercise"""
    print(f"\n=== UPDATE EXERCISE ID: {exercise_id} ===")
    # Get current exercise data first
    exercises = test_get_exercises()
    current = next((e for e in exercises if e["id"] == exercise_id), None)
    if not current:
        print(f"Exercise with ID {exercise_id} not found")
        return
    
    # Merge updates with current data
    data = {
        "name": updates.get("name", current["name"]),
        "category": updates.get("category", current["category"]),
        "time_per_set": updates.get("time_per_set", current["time_per_set"]),
        "description": updates.get("description", current["description"]),
        "reps": updates.get("reps", current["reps"]),
        "side": updates.get("side", current["side"]),
        "prompt": updates.get("prompt", current["prompt"])
    }
    response = requests.put(f"{BASE_URL}/api/exercises/{exercise_id}", json=data)
    pretty_print(response)

def test_delete_exercise(exercise_id):
    """Delete an exercise"""
    print(f"\n=== DELETE EXERCISE ID: {exercise_id} ===")
    response = requests.delete(f"{BASE_URL}/api/exercises/{exercise_id}")
    pretty_print(response)

def run_example_tests():
    """Run a series of example tests"""
    print("Starting Exercise API Tests...")
    print("Make sure the web server is running: python -m nerdouts.web")
    print("=" * 50)
    
    # 1. Get initial exercises
    initial_exercises = test_get_exercises()
    print(f"Found {len(initial_exercises)} exercises initially")
    
    # 2. Create a test exercise
    timestamp = datetime.now().strftime("%H%M%S")
    test_exercise = test_create_exercise(
        name=f"Test Exercise {timestamp}",
        category="physical_therapy",
        time_per_set=45,
        description="This is a test exercise",
        reps=3,
        side="Both",
        prompt="{name} - {side} side"
    )
    
    if test_exercise:
        exercise_id = test_exercise["id"]
        
        # 3. Update the exercise
        test_update_exercise(
            exercise_id,
            time_per_set=60,
            description="Updated description"
        )
        
        # 4. Get all exercises again
        test_get_exercises()
        
        # 5. Delete the test exercise
        test_delete_exercise(exercise_id)
        
        # 6. Verify deletion
        final_exercises = test_get_exercises()
        print(f"\nFinal exercise count: {len(final_exercises)}")
    
    # Test different side options
    print("\n=== TESTING SIDE OPTIONS ===")
    for side in ["Null", "Both", "Left", "Right"]:
        test_create_exercise(
            name=f"Side Test {side} {timestamp}",
            category="stretch",
            side=side
        )

if __name__ == "__main__":
    try:
        run_example_tests()
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to the server.")
        print("Make sure the web server is running: python -m nerdouts.web")
    except Exception as e:
        print(f"ERROR: {e}")