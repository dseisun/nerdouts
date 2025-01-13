from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
import enum
from functools import total_ordering

Base = declarative_base()


class WorkoutExercise(Base):
    __tablename__ = 'workout_exercise'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workout.id"))
    exercise_id = Column(Integer, ForeignKey("exercise.id"))
    time_per_set: Mapped[int]
    repetition: Mapped[int]
    created_date = Column(DateTime, default=datetime.now())
    workout: Mapped["Workout"] = relationship("Workout", back_populates="workout_exercises")
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="workout_exercises")


class Workout(Base):
    __tablename__ = 'workout'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    workout_exercises: Mapped[list[WorkoutExercise]] = relationship("WorkoutExercise", back_populates='workout')

    @property
    def get_total_time(self):
        return sum([wo_exc.exercise.time for wo_exc in self.workout_exercises])

    def __repr__(self):
        return ("<%s (id = %s, created_date = %s)>"
                % (self.__tablename__, self.id, self.created_date))


@total_ordering
class ExerciseCategory(enum.Enum):
    """Worth noting that the KEY is what is sent to the database
    However we keep the VALUE set to the same value as the key, because 
    we instantiate the Enum with ExerciseCategory(VALUE) when we load exercises from 
    JSON"""
    physical_therapy = "physical_therapy"
    stretch = "stretch"
    strength = "strength"
    rolling = "rolling"

    def __lt__(self, other):
        if not isinstance(other, ExerciseCategory):
            return NotImplemented
        # Define the order based on the exercise flow
        order = {
            ExerciseCategory.physical_therapy: 1,
            ExerciseCategory.stretch: 2,
            ExerciseCategory.strength: 3,
            ExerciseCategory.rolling: 4
        }
        return order[self] < order[other]


class Exercise(Base):
    __tablename__ = 'exercise'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_date: Mapped[datetime] = mapped_column(default=datetime.now())
    name: Mapped[str] = mapped_column(unique=True)
    category_id: Mapped[ExerciseCategory] = mapped_column(Enum(ExerciseCategory))
    side: Mapped[str]
    default_time: Mapped[int]
    repetition: Mapped[int]
    prompt: Mapped[str]
    long_desc: Mapped[str]
    workout_exercises: Mapped[list[WorkoutExercise]] = relationship("WorkoutExercise", back_populates='exercise')

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

