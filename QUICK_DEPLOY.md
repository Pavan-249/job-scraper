# ⚡ Quick Deployment to GitHub Actions (5 minutes)

## Step 1: Initialize Git (if not already done)
```bash
cd "/Users/pavankumar_s/Desktop/Job Scrapper"
git init
git add .
git commit -m "Initial commit - Fast job scraper"
```

## Step 2: Create GitHub Repo & Push
1. Go to https://github.com/new
2. Create a **private** repository (e.g., "job-scraper")
3. Don't initialize with README
4. Copy the repo URL

```bash
git remote add origin https://github.com/YOUR_USERNAME/job-scraper.git
git branch -M main
git push -u origin main
```

## Step 3: Add Secrets to GitHub
1. Go to your repo: https://github.com/YOUR_USERNAME/job-scraper
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

  

## Step 4: Enable GitHub Actions
1. Go to **Actions** tab in your repo
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow will automatically start running every 5 minutes!

## ✅ Done!
- Your scraper runs every 5 minutes in GitHub's cloud (FREE!)
- You'll get emails when new jobs are found
- Check **Actions** tab to see logs
- No laptop needed - runs 24/7 automatically!

## Test Locally First (Optional)
```bash
pip3 install -r requirements.txt
python3 main.py --run-once
```

Expected time: **20-30 seconds** for full search! ⚡

