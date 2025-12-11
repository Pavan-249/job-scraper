#!/bin/bash
# Script to run the job scraper once (for cron usage)

cd "$(dirname "$0")"
/usr/bin/python3 main.py --run-once

