#!/bin/bash

cd /var/www/pow.palzoltan.flask

# Activate the venv
/etc/poetry/bin/poetry shell

# Execute the job
/etc/poetry/bin/poetry run python -m jobs.daily.rss_reader

# Deactivate the venv
#deactivate
