import enum
import subprocess
import time
from cached_property import cached_property
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import dbus
import yaml
secrets = yaml.load(open('secrets.yaml', 'r'))


engine = create_engine(secrets['sqlalchemy_connection_string'], echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class MusicIface(object):
    logger = logging.Logger('workout')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    @cached_property
    def iface(self):
        session_bus = dbus.SessionBus()
        player = session_bus.get_object('org.mpris.clementine', '/Player')
        return dbus.Interface(player, dbus_interface='org.freedesktop.MediaPlayer')

    def say(self, sentence, pause_music=True):
        if pause_music:
            self.iface.Pause()
        subprocess.call('echo "' + sentence + '"| festival --tts', shell=True)
        self.logger.info(sentence)
        if pause_music:
            self.iface.Play()   


class WorkoutExercise(Base):
    __tablename__ = 'workout_exercise'
    workout_exercise_id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("workout.id"))
    exercise_id = Column(Integer, ForeignKey("exercise.id"))
    created_date = Column(DateTime, default=datetime.now())
    workout = relationship("Workout", back_populates="workout_exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")


class Workout(Base, MusicIface):
    __tablename__ = 'workout'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    workout_exercises = relationship("WorkoutExercise", back_populates='workout')

    @property
    def get_total_time(self):
        return sum([wo_exc.exercise.time for wo_exc in self.workout_exercises])


    def run_workout(self):
        for e in self.workout_exercises:
            e.created_date = datetime.now()
            e.exercise.run()
        self.say('Workout finished')

    def __repr__(self):
        return ("<%s (id = %s, created_date = %s)>"
                % (self.__tablename__, self.id, self.created_date))


class ExerciseCategory(Base):
    __tablename__ = 'exercise_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))


class Exercise(Base, MusicIface):
    __tablename__ = 'exercise'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    name = Column(String(255))
    category_id = Column(ForeignKey("exercise_category.id"))
    side = Column(String(10))
    default_time = Column(Integer)
    repetition = Column(Integer)
    prompt = Column(String(1024))    
    workout_exercises = relationship("WorkoutExercise", back_populates='exercise')

    def sentence(self, side=''):
        return self.prompt.format(name=self.name, side=side)

    @property
    def sides(self):
        if self.side == 'Both':
            return ['left', 'right']
        else:
            return [self.side]

    def run(self):
        for side in self.sides:
            for i in range(self.repetition):
                self.say(self.sentence(side=side))
                self.countdown(self.default_time)

    def countdown(self, exc_time):
        for sec in range(exc_time):
            self.logger.info("{0} seconds until the next exercise".format(exc_time-sec))
            if exc_time - sec == 10:
                self.say("10 Seconds left", pause_music=False)
            time.sleep(1)

    @property
    def time(self):
        return self.default_time * self.repetition * len(self.sides)

    def __repr__(self):
        return ("<%s (name = %s, repetition = %s, sides = %s, default_time = %s)>"
                % (self.__tablename__, self.name, self.repetition, self.sides, self.default_time))


