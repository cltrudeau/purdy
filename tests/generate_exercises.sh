#!/bin/bash
echo "all_console"
./capture_exercise.py all_console
mv flipbook.json exercise_data/all_console.json

echo "append"
./capture_exercise.py append
mv flipbook.json exercise_data/append.json

echo "bash_console"
./capture_exercise.py bash_console
mv flipbook.json exercise_data/bash_console.json

echo "cols"
./capture_exercise.py cols
mv flipbook.json exercise_data/cols.json

echo "compact"
./capture_exercise.py compact
mv flipbook.json exercise_data/compact.json

echo "docstring"
./capture_exercise.py docstring
mv flipbook.json exercise_data/docstring.json

echo "exec"
./capture_exercise.py exec
mv flipbook.json exercise_data/exec.json

echo "fold"
./capture_exercise.py fold
mv flipbook.json exercise_data/fold.json

echo "highlight"
./capture_exercise.py highlight
mv flipbook.json exercise_data/highlight.json

echo "insert"
./capture_exercise.py insert
mv flipbook.json exercise_data/insert.json

echo "lines"
./capture_exercise.py lines
mv flipbook.json exercise_data/lines.json

echo "mixed"
./capture_exercise.py mixed
mv flipbook.json exercise_data/mixed.json

echo "mls_type"
./capture_exercise.py mls_type
mv flipbook.json exercise_data/mls_type.json

echo "movie_console"
./capture_exercise.py movie_console
mv flipbook.json exercise_data/movie_console.json

echo "remove"
./capture_exercise.py remove
mv flipbook.json exercise_data/remove.json

echo "replace"
./capture_exercise.py replace
mv flipbook.json exercise_data/replace.json

echo "sleep"
./capture_exercise.py sleep
mv flipbook.json exercise_data/sleep.json

echo "src_change"
./capture_exercise.py src_change
mv flipbook.json exercise_data/src_change.json

echo "split_long"
./capture_exercise.py split_long
mv flipbook.json exercise_data/split_long.json

echo "swipe"
./capture_exercise.py swipe
mv flipbook.json exercise_data/swipe.json

echo "tall"
./capture_exercise.py tall
mv flipbook.json exercise_data/tall.json

echo "triple"
./capture_exercise.py triple
mv flipbook.json exercise_data/triple.json

echo "type_console"
./capture_exercise.py type_console
mv flipbook.json exercise_data/type_console.json
