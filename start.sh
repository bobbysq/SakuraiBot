#!/bin/bash

# Pretty much copy-pasted from reddit-xkcdbot, with slight changes

# Kill if started
export SAKURAIPID=`ps aux | grep '__init__.py' | grep -v grep | awk '{print($2)}'`

if [ -n "$SAKURAIPID" ]; then
  echo "Killing old process "$SAKURAIPID"."
  kill $SAKURAIPID
fi

# Update from git
echo "Pulling latest git version"
git pull

# Start
echo "Starting"
cd src
nohup python __init__.py >../nohup.out 2>&1 &
disown

sleep 1
export SAKURAIPID=`ps aux | grep '__init__.py' | grep -v grep | awk '{print($2)}'`
if [ -n "$SAKURAIPID" ]; then
  echo "Running correctly."
else
  echo "ERROR: Script stopped."
fi
