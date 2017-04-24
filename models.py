from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WorkoutExercise(Base):
    __tablename__ = 'workout_exercise'
    workout_exercise_id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("workout.id"))
    exercise_id = Column(Integer, ForeignKey("exercise.id"))
    time_per_set = Column(Integer)
    repetition = Column(Integer)
    created_date = Column(DateTime, default=datetime.now())
    workout = relationship("Workout", back_populates="workout_exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")


class Workout(Base):
    __tablename__ = 'workout'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    workout_exercises = relationship("WorkoutExercise", back_populates='workout')

    @property
    def get_total_time(self):
        return sum([wo_exc.exercise.time for wo_exc in self.workout_exercises])

    def __repr__(self):
        return ("<%s (id = %s, created_date = %s)>"
                % (self.__tablename__, self.id, self.created_date))


class ExerciseCategory(Base):
    __tablename__ = 'exercise_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))


class Exercise(Base):
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

    @property
    def time(self):
        return self.default_time * self.repetition * len(self.sides)

    def __repr__(self):
        return ("<%s (name = %s, repetition = %s, sides = %s, default_time = %s)>"
                % (self.__tablename__, self.name, self.repetition, self.sides, self.default_time))


