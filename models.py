import enum
import subprocess
import time
from cached_property import cached_property
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import dbus
import yaml
secrets = yaml.load(open('secrets.yaml', 'r'))


engine = create_engine(secrets['sqlalchemy_connection_string'], echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)


association_table = Table('workout_exercises', Base.metadata,
    Column('created_date', DateTime, default=datetime.now()),
    Column('workout_id', Integer, ForeignKey('workout.id')),
    Column('exercise_id', Integer, ForeignKey('exercise.id'))
)


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


class Workout(Base, MusicIface):
    __tablename__ = 'workout'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    exercises = relationship("Exercise",
                             secondary=association_table,
                             back_populates='workouts')

    @property
    def get_total_time(self):
        return sum([exc.time for exc in self.exercises])


    def run_workout(self):
        for e in self.exercises:
            e.run()
        self.say('Workout finished')

    def __repr__(self):
        return ("<%s (id = %s, created_date = %s)>"
                % (self.__tablename__, self.id, self.created_date))


categories = {
    'physical_therapy': 'physical_therapy',
    'stretch': 'stretch',
    'strength': 'strength',
    'rolling': 'rolling'}

Categories = enum.Enum('Categories', categories)


class Exercise(Base, MusicIface):
    __tablename__ = 'exercise'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    name = Column(String(255))
    category = Column(Enum(Categories))
    side = Column(String(10))
    default_time = Column(Integer)
    repetition = Column(Integer)
    prompt = Column(String(1024))
    
    workouts = relationship("Workout",
                            secondary=association_table,
                            back_populates='exercises')


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

