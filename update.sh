#!/bin/sh
cd /app
git config --global --add safe.directory /app
git pull https://github.com/lenartkladnik/tutorstvo-website

kill 1 # Kill the docker container so it restarts itself
