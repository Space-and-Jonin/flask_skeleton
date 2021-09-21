#!/bin/sh
gunicorn app.wsgi:app -b 0.0.0.0:5000
#gunicorn app.wsgi:app -w 2 --threads 2 -b 0.0.0.0:8000
