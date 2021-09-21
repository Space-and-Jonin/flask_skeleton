#!/bin/sh
flask db upgrade
gunicorn app.wsgi:app -b 0.0.0.0:5000 --log-level error --error-logfile gunicorn.error.log --access-logfile log.log
