#!/bin/bash
echo "all_console"
./capture_sample.py all_console
mv cells.json samples_data/all_console.json
echo "append"
./capture_sample.py append
mv cells.json samples_data/append.json
echo "bash_console"
./capture_sample.py bash_console
mv cells.json samples_data/bash_console.json
echo "cols"
./capture_sample.py cols
mv cells.json samples_data/cols.json
echo "docstring"
./capture_sample.py docstring
mv cells.json samples_data/docstring.json
echo "exec"
./capture_sample.py exec
mv cells.json samples_data/exec.json
echo "highlight"
./capture_sample.py highlight
mv cells.json samples_data/highlight.json
echo "insert"
./capture_sample.py insert
mv cells.json samples_data/insert.json
echo "lines"
./capture_sample.py lines
mv cells.json samples_data/lines.json
echo "mixed"
./capture_sample.py mixed
mv cells.json samples_data/mixed.json
echo "mls_type"
./capture_sample.py mls_type
mv cells.json samples_data/mls_type.json
echo "movie_console"
./capture_sample.py movie_console
mv cells.json samples_data/movie_console.json
echo "remove"
./capture_sample.py remove
mv cells.json samples_data/remove.json
echo "replace"
./capture_sample.py replace
mv cells.json samples_data/replace.json
echo "split_long"
./capture_sample.py split_long
mv cells.json samples_data/split_long.json
echo "swipe"
./capture_sample.py swipe
mv cells.json samples_data/swipe.json
echo "tall"
./capture_sample.py tall
mv cells.json samples_data/tall.json
echo "triple"
./capture_sample.py triple
mv cells.json samples_data/triple.json
echo "type_console"
./capture_sample.py type_console
mv cells.json samples_data/type_console.json
