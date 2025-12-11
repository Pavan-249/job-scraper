# Quick Start Guide 🚀

Get your job scraper running in 5 minutes!

## Step 1: Install Dependencies

```bash
cd "/Users/pavankumar_s/Desktop/Job Scrapper"
pip3 install -r requirements.txt
```

## Step 2: Set Up Email

1. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Gmail:
   ```
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_gmail_app_password
   EMAIL_RECIPIENT=your_email@gmail.com
   ```

3. **Get Gmail App Password:**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Go to App Passwords
   - Generate password for "Mail"
   - Copy the 16-character password to `.env`

## Step 3: Add Companies

Edit `config.py` and add companies to the `COMPANIES` list:
```python
COMPANIES = [
    "Google",
    "Microsoft",
    # ... add your companies
]
```

## Step 4: Test It

Run once to test:
```bash
python3 main.py --run-once
```

## Step 5: Run Continuously

**Option A: Keep Terminal Open**
```bash
python3 main.py
```

**Option B: Run in Background (macOS)**
```bash
nohup python3 main.py > scraper.log 2>&1 &
```

**Option C: Use Cron (Best for Always-On)**

1. Edit crontab:
   ```bash
   crontab -e
   ```

2. Add this line (runs every 5 minutes):
   ```
   */5 * * * * cd "/Users/pavankumar_s/Desktop/Job Scrapper" && /usr/bin/python3 main.py --run-once >> scraper.log 2>&1
   ```

3. Check logs:
   ```bash
   tail -f scraper.log
   ```

## You're Done! 🎉

The scraper will now check every 5 minutes and email you when new jobs are found!

