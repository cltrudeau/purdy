#!/bin/bash

echo "============================================================"
echo "== pyflakes =="
pyflakes src tests extras/samples extras/tools

echo "============================================================"
echo "== loggers =="
pygrep "logger" | grep -v "#" | grep -v "extras/tools"
