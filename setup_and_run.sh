#!/bin/bash

echo "Installing required dependencies..."
pip install -r requirements.txt

echo "Starting the application on port 5007..."
export FLASK_APP=run.py
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5007