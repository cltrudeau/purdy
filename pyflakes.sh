#!/bin/bash

echo "============================================================"
echo "== pyflakes =="
pyflakes purdy tests extras/samples extras/tools

echo "============================================================"
echo "== loggers =="
pygrep "logger" | grep -v "#" | grep -v "extras/tools"
