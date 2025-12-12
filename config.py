"""
Configuration file for the job scraper
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration (using Gmail SMTP - free)
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "pavancseds@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "zkne yuqq uycz qckr")  # Gmail App Password
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "pavancseds@gmail.com")

# SMTP Configuration (Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Job Search Criteria
SEARCH_KEYWORDS = [
    "data analyst intern",
    "data engineer intern", 
    "data architect intern"
]

REQUIRED_SKILLS = ["python", "sql"]

LOCATION = "United States"
YEAR = "2026"
SEASON = "summer"

# Companies list - 1000+ companies known for hiring interns
# Includes big tech, Fortune 500, Y Combinator startups, and growing tech companies
from companies_list import COMPANIES_LIST

# For testing: use first 100 companies
COMPANIES = COMPANIES_LIST[:100]  # Test with 100 companies first
# COMPANIES = COMPANIES_LIST  # Uncomment to use all companies

# Storage file for tracking seen jobs
JOBS_DB_FILE = "seen_jobs.json"

# Scraping settings
CHECK_INTERVAL_MINUTES = 5

# Only show jobs posted within this many hours (to catch them instantly!)
# Set to 0.5 hours (30 minutes) for very recent postings, or 24 hours if date not available
MAX_JOB_AGE_HOURS = 0.5  # 30 minutes for jobs with timestamp
MAX_JOB_AGE_HOURS_FALLBACK = 24  # 24 hours if no timestamp available

