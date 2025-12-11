# 🚀 Remote Deployment Guide

Deploy your job scraper to run automatically in the cloud for FREE!

## Option 1: GitHub Actions (Recommended - FREE)

### Setup Steps:

1. **Create a GitHub Repository**
   ```bash
   cd "/Users/pavankumar_s/Desktop/Job Scrapper"
   git init
   git add .
   git commit -m "Initial commit - Job scraper"
   ```

2. **Push to GitHub**
   - Create a new repository on GitHub (make it private)
   - Push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/job-scraper.git
   git push -u origin main
   ```

3. **Add GitHub Secrets**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Click "New repository secret" and add:
     - `EMAIL_SENDER`: `pavancseds@gmail.com`
     - `EMAIL_PASSWORD`: `zkne yuqq uycz qckr`
     - `EMAIL_RECIPIENT`: `pavancseds@gmail.com`

4. **Enable GitHub Actions**
   - The workflow file (`.github/workflows/job-scraper.yml`) is already included
   - It will automatically run every 5 minutes
   - You can also trigger manually: Actions tab → "Job Scraper" → Run workflow

### Benefits:
- ✅ **100% FREE** - Unlimited runs on GitHub Actions
- ✅ **Runs every 5 minutes automatically**
- ✅ **No laptop needed** - Runs in GitHub's cloud
- ✅ **Email notifications** sent directly to you
- ✅ **No setup needed** after initial configuration

---

## Option 2: Railway (Alternative - FREE tier available)

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project → Deploy from GitHub repo
4. Add environment variables:
   - `EMAIL_SENDER`
   - `EMAIL_PASSWORD`
   - `EMAIL_RECIPIENT`
5. Set up cron job or use Railway's scheduler

---

## Option 3: Render (Alternative - FREE tier)

1. Go to [render.com](https://render.com)
2. Create a new Cron Job
3. Connect your GitHub repo
4. Set schedule: `*/5 * * * *` (every 5 minutes)
5. Add environment variables
6. Deploy!

---

## Local Testing

To test locally before deploying:

```bash
# Install dependencies
pip3 install -r requirements.txt

# Test run (should complete in ~30 seconds)
python3 main.py --run-once
```

---

## Speed Optimizations

The scraper is optimized for speed:
- ⚡ **Parallel execution** - 50 concurrent searches
- ⚡ **No delays** - Removed all sleep/wait times
- ⚡ **RSS-only** - Skips slow HTML scraping
- ⚡ **Early filtering** - Filters by date before processing
- ⚡ **Limited results** - Only checks top 10 most recent per search

Expected completion time: **20-30 seconds** for 1,182 companies × 3 keywords

---

## Monitoring

- Check GitHub Actions logs: Repo → Actions tab
- Check email for job notifications
- View `seen_jobs.json` artifact in GitHub Actions (optional)

---

## Troubleshooting

**Workflow not running?**
- Check Actions tab for errors
- Verify secrets are set correctly
- Check workflow file syntax

**No emails received?**
- Verify email secrets are correct
- Check Actions logs for email errors
- Make sure 2-Step Verification is enabled on Gmail

**Scraper too slow?**
- Reduce `max_workers` in `scraper.py` if hitting rate limits
- Reduce `MAX_JOB_AGE_HOURS` to search fewer jobs
- GitHub Actions has 2-minute timeout (should be plenty)

