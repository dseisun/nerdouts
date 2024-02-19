from argparse import Namespace
import unittest
from unittest.mock import patch
import run_workout


class TestArgparse(unittest.TestCase):

    @patch('sys.argv', ['main_script.py', '-t', '30'])
    def test_time_argument(self):
        args = run_workout.parse_args()
        self.assertEqual(args.time, 30)

    @patch('sys.argv', ['main_script.py', '-t', '30', '-w', 'custom_config.json'])
    def test_workout_argument(self):
        args = run_workout.parse_args()
        self.assertEqual(args.workout, 'custom_config.json')

    @patch('sys.argv', ['main_script.py', '-t', '30', '-d'])
    def test_debug_argument(self):
        args = run_workout.parse_args()
        self.assertTrue(args.debug)


class TestSubParsers(unittest.TestCase):
    @patch('sys.argv', ['run_workout.py', 'dynamic', '-t', '30'])
    def test_baseline(self):
        args: Namespace = run_workout.parse_subargs()
        self.assertFalse(args.debug)
        
        

if __name__ == '__main__':
    unittest.main()
