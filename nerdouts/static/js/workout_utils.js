// Common workout utility functions

function calculateWorkoutTime(exercises) {
    // For workout.html, exercises is an array of {default_time, repetition, sides} objects
    // For create_static_workout.html, exercises is an array of {time} objects
    const totalSeconds = exercises.reduce((total, exercise) => {
        if ('time' in exercise) {
            // Used by create_static_workout.html
            return total + exercise.time;
        } else {
            // Used by workout.html
            const sidesCount = exercise.side === 'Both' ? 2 : 1;
            return total + (exercise.default_time * exercise.repetition * sidesCount);
        }
    }, 0);
    
    return Math.round(totalSeconds / 60); // Return minutes
}

function formatWorkoutTime(minutes) {
    return `Total workout time: ${minutes} minutes`;
}
