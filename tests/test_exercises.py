import json
from pathlib import Path
from unittest import TestCase

from tests.capture_exercise import run_exercise


class TestExercises(TestCase):
    def _run_exercises(self, exercise_name_pattern: str) -> None:

        exercises = ["all_console", "append", "bash_console", "cols", "compact",
            "docstring", "exec", "fold", "highlight", "insert", "lines",
            "maxheight", "mixed", "mls_type", "movie_console", "remove",
            "replace", "sleep", "split_long", "src_change", "swipe", "tall",
            "triple", "type_console", ]

        exercise_data = Path(__file__).parent / "exercise_data"

        for exercise in exercises:
            # load stored expected results
            filename = exercise_data / f"{exercise}.json"
            with open(filename) as f:
                expected = json.load(f)

            # load the module and run the actions using the ExerciseScreen
            pages = run_exercise(exercise_name_pattern.format(exercise))

            try:
                self.assertEqual(expected, pages, 
                    msg=f"Compare failed for exercise: {exercise}")
            finally:
                pages.insert(0, f"******** Exercise: {exercise}")
                with open("last_exercise.json", "w") as f:
                    json.dump(pages, f, indent=2)

    def test_exercises(self):
        self._run_exercises("{}")

    def test_exercises_with_builder(self):
        self._run_exercises("{}_builder")
