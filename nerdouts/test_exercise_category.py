from nerdouts.models import ExerciseCategory

def test_exercise_category_ordering():
    # Test ordering
    assert ExerciseCategory.physical_therapy < ExerciseCategory.stretch
    assert ExerciseCategory.stretch < ExerciseCategory.strength
    assert ExerciseCategory.strength < ExerciseCategory.rolling
    
    # Test sorting
    categories = [
        ExerciseCategory.rolling,
        ExerciseCategory.physical_therapy,
        ExerciseCategory.strength,
        ExerciseCategory.stretch
    ]
    sorted_categories = sorted(categories)
    assert sorted_categories == [
        ExerciseCategory.physical_therapy,
        ExerciseCategory.stretch,
        ExerciseCategory.strength,
        ExerciseCategory.rolling
    ]

if __name__ == "__main__":
    test_exercise_category_ordering()
    print("All tests passed!")
