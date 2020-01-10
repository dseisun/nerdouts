import json
import logging


class Config(object):
    """Object representing a config file/total_time pair. Since these are both arguments to the
    application, it's the object stating the runtime config of the workout
    It explicitly doesn't talk to the db
    Purpose is to have a single interface for getting properies of a config file
    and a good state store for it"""

    def __init__(self, config_file_path, total_time):
        with open(config_file_path) as data_file:
            self.workout_config = json.load(data_file)
        self.total_time = total_time

    @property
    def exercise_category_times(self):
        """Returns a map of category names to tatal times"""
        cat_times = {}
        for category in self.workout_config['categories']:
            cat_times[category['name']] = self.total_time * 60 * category['weight']
        self.workout_config['categories']
        total_cat_weight = sum(map(lambda x: x['weight'], self.workout_config['categories']))
        # Quick validation that the category weights add up to 100%
        if total_cat_weight != 1:
            logging.warning('Total category weight does not add up to 100%. Adds up to %s' %
                            total_cat_weight)
        return cat_times

    @property
    def whitelisted_exercises(self):
        """Exercises that _have_ to be included in the workout.
        Expected behaviour is to add all the exercises even if it goes over time"""
        return self.workout_config.get("whitelist", [])

    @property
    def blacklisted_exercises(self):
        """Exercises that _have_ to be excluded in the workout.
        This should return a list of exercises that can't be added.
        TODO: Currently input is just a list of id's from the config, but we can expand that to
        blacklisting categories and being more dynamic
        """
        return self.workout_config.get("blacklist", [])