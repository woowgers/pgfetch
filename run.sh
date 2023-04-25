#!/bin/sh

cd src

if [ $# -eq 0 ]; then
  python -m project.main
elif [ "$1" = "debug" ]; then
  python -m pdb -m project.main
fi
