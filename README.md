# 🎯 Job Scraper - Summer 2026 Internship Finder

Automatically monitors job listings from **1,182+ companies** and sends email notifications when new matching jobs are posted.

## Features

- ✅ Searches **1,182+ companies** for **Summer 2026 internships** in the US
- ✅ Filters for: **Data Analyst Intern**, **Data Engineer Intern**, **Data Architect Intern**
- ✅ Requires **Python and SQL** in job description
- ✅ **Lightning fast**: Completes full search in **20-30 seconds**
- ✅ Only shows jobs posted in last **24 hours** (catches them instantly!)
- ✅ Checks every **5 minutes** automatically via GitHub Actions
- ✅ **Runs in cloud** (FREE) - No laptop needed!
- ✅ Sends email notifications for **new jobs only**
- ✅ Uses **100% free tools** (Indeed RSS feeds, Gmail SMTP, GitHub Actions)

## 🚀 Quick Deployment (Recommended: GitHub Actions)

**For FREE remote execution that runs automatically every 5 minutes:**

See **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** for step-by-step instructions (takes 5 minutes!)

**Benefits:**
- ✅ Runs in GitHub's cloud (FREE)
- ✅ No laptop needed - runs 24/7 automatically
- ✅ Completes in 20-30 seconds
- ✅ Emails you when new jobs are found

---

## Local Testing (Optional)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Run

```bash
python3 main.py --run-once
```

Expected completion: **20-30 seconds** for 1,182 companies × 3 keywords

### 3. Configure Email (if testing locally)

Email is already configured in `config.py`, but you can override with environment variables if needed.

## How It Works

1. **Parallel execution** - Uses 50 concurrent workers to search all companies simultaneously
2. **Scrapes Indeed RSS feeds** for each company + keyword combination (sorted by most recent first)
3. **Filters jobs** based on:
   - **Must be posted within last 24 hours** (to catch listings instantly!)
   - Must contain "intern" in title
   - Must match one of: data analyst intern, data engineer intern, data architect intern
   - Job description must mention both "Python" and "SQL"
   - Location: United States
   - Looking for Summer 2026 internships

4. **Tracks seen jobs** in `seen_jobs.json` to avoid duplicates

5. **Sends email** only for new jobs that haven't been seen before, with posting time included

### Speed Optimizations:
- ⚡ **Parallel execution** - 50 concurrent searches
- ⚡ **No delays** - Removed all sleep/wait times
- ⚡ **RSS-only** - Skips slow HTML scraping
- ⚡ **Early filtering** - Filters by date before processing
- ⚡ **Limited results** - Only checks top 10 most recent per search

## Files

- `main.py` - Main entry point and scheduler
- `scraper.py` - Job scraping logic using Indeed RSS feeds
- `job_tracker.py` - Tracks seen jobs to detect new ones
- `email_notifier.py` - Sends email notifications
- `config.py` - Configuration settings
- `seen_jobs.json` - Database of seen jobs (auto-generated)
- `.env` - Your email credentials (not in git)

## Notes

- The scraper is respectful with rate limiting (delays between requests)
- Uses free Indeed RSS feeds (no API key needed)
- All tools used are completely free
- Jobs are tracked by a unique ID based on title + company + URL

## Troubleshooting

**Email not sending?**
- Check your Gmail App Password is correct
- Ensure 2-Step Verification is enabled
- Check that EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECIPIENT are set in .env

**Not finding jobs?**
- Make sure companies are added to the COMPANIES list in config.py
- Check that your search criteria aren't too restrictive
- Verify Indeed RSS feeds are accessible

**Want to reset seen jobs?**
- Delete `seen_jobs.json` and it will be recreated

## Good Luck! 🚀

Hope you find the perfect internship!

