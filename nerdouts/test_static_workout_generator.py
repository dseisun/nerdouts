import json
from unittest.mock import patch
import os
import pytest
import nerdouts.generate_static_workout

TEST_EXERCISE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_exercises.json')

@pytest.fixture
def exercises():
    return json.load(open(TEST_EXERCISE_PATH, 'r'))

def test_exercises_length(exercises):
    assert len(exercises) == 63

@patch('generate_static_workout.input')
def test_static_workout_generation(mock_input):
    mock_input.side_effect = [1, 2, 0, -1]
    output = generate_static_workout.static_workout_generator(TEST_EXERCISE_PATH)
    expected_output = ['get_by_name("Clamshells")', 'get_by_name("High Kicks")', 'get_by_name("Butt Kickers")']
    assert output == expected_output

