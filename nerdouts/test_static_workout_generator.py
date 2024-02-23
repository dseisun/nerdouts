import unittest
from unittest.mock import patch
import json
import generate_static_workout
import os
TEST_EXERCISE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_exercises.json')
exercises = json.load(open(TEST_EXERCISE_PATH, 'r'))

class TestLoadExercisesFromJson(unittest.TestCase):
    def test_is_expected_len(self):
        self.assertEqual(len(exercises), 63)


class TestGenerateStaticWorkout(unittest.TestCase):
    
    @patch('generate_static_workout.input')
    def setUp(self, mock_input):
        mock_input.side_effect = [1,2,0, -1]
        self.output = generate_static_workout.static_workout_generator(TEST_EXERCISE_PATH)
        print(self.output)
    
    def test_content(self):
        expected_output = ['get_by_name("Clamshells")', 'get_by_name("High Kicks")', 'get_by_name("Butt Kickers")']
        self.assertEqual(self.output, expected_output)

