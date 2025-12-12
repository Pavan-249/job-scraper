"""
Test script to check Trimble internships and send email
"""
from datetime import datetime
from scraper import JobScraper
from job_tracker import JobTracker
from email_notifier import EmailNotifier
from config import JOBS_DB_FILE

def test_trimble():
    """Test search for Trimble internships"""
    print("="*60)
    print("🧪 Testing Trimble Internship Search")
    print("="*60)
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    try:
        # Initialize components
        scraper = JobScraper(max_workers=10)  # Use fewer workers for testing
        tracker = JobTracker(JOBS_DB_FILE)
        notifier = EmailNotifier()
        
        # Test search for Trimble only
        print("🔍 Searching for Trimble internships...\n")
        
        # Create test combinations - just Trimble
        from config import SEARCH_KEYWORDS
        test_companies = ["Trimble"]
        combinations = [(company, keyword) for company in test_companies for keyword in SEARCH_KEYWORDS]
        
        all_jobs = []
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Execute in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_combo = {executor.submit(scraper._search_single_combination, combo): combo 
                              for combo in combinations}
            
            for future in as_completed(future_to_combo):
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                    if jobs:
                        for job in jobs:
                            print(f"  ✅ Found: {job['title']} at {job['company']}")
                            print(f"     🔗 {job['url']}")
                            print(f"     📅 Posted: {job.get('published', 'N/A')}\n")
                except Exception as e:
                    print(f"  ⚠️  Error: {str(e)}")
        
        print(f"\n📊 Total jobs found for Trimble: {len(all_jobs)}")
        
        if all_jobs:
            print("\n" + "="*60)
            print("📧 Sending email notification...")
            print("="*60)
            
            # Filter for new jobs (or send all for testing)
            new_jobs = tracker.get_new_jobs(all_jobs)
            
            if new_jobs:
                print(f"📬 Sending email for {len(new_jobs)} new job(s)...")
                notifier.send_notification(new_jobs)
                print("✅ Test completed - Check your email!")
            else:
                print("ℹ️  All jobs already seen. Sending anyway for testing...")
                # For testing, send all jobs even if seen
                notifier.send_notification(all_jobs)
                print("✅ Test completed - Check your email!")
        else:
            print("\n⚠️  No Trimble internships found matching criteria")
            print("   Criteria:")
            print("   - Must contain 'intern' in title")
            print("   - Must match: data analyst/engineer/architect intern")
            print("   - Must mention Python AND SQL")
            print("   - Posted in last 48 hours")
        
        print("\n" + "="*60)
        print(f"✅ Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_trimble()




