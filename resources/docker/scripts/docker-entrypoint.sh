#!/bin/bash

# Run the Flask app:
if [[ "${UWSGI_FRAMEWORK}" == "werkzeug" ]]
then
    python3 /slate/main.py
else
    gunicorn -w 2 -b 0.0.0.0:$FLASK_PORT main:app
fi
