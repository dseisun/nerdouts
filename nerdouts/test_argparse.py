from argparse import Namespace
import unittest
from unittest.mock import patch
import run_workout



class TestSubParsers(unittest.TestCase):
    @patch('sys.argv', ['run_workout.py', 'dynamic', '-t', '30'])
    def test_baseline(self):
        args: Namespace = run_workout.parse_args()
        self.assertFalse(args.debug)
        

if __name__ == '__main__':
    unittest.main()
