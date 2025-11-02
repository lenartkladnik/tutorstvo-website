#!/bin/bash

echo "Starting tutorstvo-website-server..."
flask db upgrade
python3 app.py
