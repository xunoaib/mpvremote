#!/usr/bin/bash

# unless otherwise specified, this ensures cache will be stored under this directory
cd `dirname "$0"`

# python -m src.mpvremote.webserver   # debugging
gunicorn src.mpvremote.webserver:app  # production
