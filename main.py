"""
Main entry point for the job scraper
For GitHub Actions: runs once via --run-once flag
"""
import sys
from datetime import datetime
from scraper import JobScraper
from job_tracker import JobTracker
from email_notifier import EmailNotifier
from config import JOBS_DB_FILE

def check_for_new_jobs():
    """Main function to check for new jobs"""
    print(f"\n{'='*60}")
    print(f"⏰ Job Check Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # Initialize components
        scraper = JobScraper()
        tracker = JobTracker(JOBS_DB_FILE)
        notifier = EmailNotifier()
        
        # Scrape all jobs
        all_jobs = scraper.scrape_all_jobs()
        
        # Filter for new jobs
        new_jobs = tracker.get_new_jobs(all_jobs)
        
        if new_jobs:
            print(f"\n🎉 Found {len(new_jobs)} NEW job(s)!")
            for job in new_jobs:
                print(f"  ✨ {job['title']} at {job['company']}")
                print(f"     🔗 {job['url']}\n")
            
            # Send email notification
            notifier.send_notification(new_jobs)
        else:
            print("\n✅ No new jobs found this time. Keep checking!")
        
        print(f"\n{'='*60}")
        print(f"✅ Job check completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error during job check: {str(e)}\n")
        import traceback
        traceback.print_exc()

def main():
    """Main function - just runs once (scheduling handled by GitHub Actions)"""
    print("\n" + "="*60)
    print("🚀 Job Scraper - Single Run")
    print("="*60)
    print(f"📅 Checking for: Summer 2026 Internships")
    print(f"🎯 Roles: Data Analyst/Engineer/Architect Intern")
    print(f"🔧 Skills: Python & SQL required")
    print("="*60 + "\n")
    
    check_for_new_jobs()

if __name__ == "__main__":
    try:
        # Always run once (GitHub Actions handles scheduling)
        if "--run-once" in sys.argv:
            check_for_new_jobs()
        else:
            main()
    except KeyboardInterrupt:
        print("\n\n👋 Job scraper stopped by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

