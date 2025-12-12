"""
High-speed job scraper with parallel execution - scrapes company career pages directly
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import SEARCH_KEYWORDS, REQUIRED_SKILLS, LOCATION, YEAR, SEASON, COMPANIES, MAX_JOB_AGE_HOURS
from company_career_scraper import CompanyCareerScraper

class JobScraper:
    def __init__(self, max_workers=30):
        self.max_age_hours = MAX_JOB_AGE_HOURS
        self.max_workers = max_workers  # Parallel workers for speed
        self.career_scraper = CompanyCareerScraper()
    
    def _search_single_company(self, company: str) -> List[Dict[str, Any]]:
        """Search single company's career page (for parallel execution)"""
        if not company.strip():
            return []
        
        try:
            jobs = self.career_scraper.scrape_company_internships(company)
            if jobs:
                print(f"  ✅ Found {len(jobs)} internship(s) at {company}")
                for job in jobs:
                    print(f"     • {job['title']}")
            return jobs
        except Exception as e:
            # Silently fail for individual companies to not interrupt the process
            return []
    
    def scrape_all_jobs(self) -> List[Dict[str, Any]]:
        """Scrape jobs from all company career pages - PARALLEL EXECUTION"""
        print(f"\n🚀 Starting parallel job search across {len(COMPANIES)} companies...")
        print(f"📋 Searching company career pages directly (not Indeed)")
        print(f"🔧 Looking for data-related internships (Python/SQL or data technologies)")
        print(f"📍 Location: {LOCATION}")
        print(f"📅 Looking for: {SEASON} {YEAR} internships")
        print(f"⏰ Only showing jobs posted in the last {self.max_age_hours} hours")
        print(f"⚡ Using {self.max_workers} parallel workers for speed...\n")
        
        all_jobs = []
        start_time = datetime.now()
        
        # Execute in parallel - one task per company
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_company = {executor.submit(self._search_single_company, company): company 
                               for company in COMPANIES}
            
            completed = 0
            for future in as_completed(future_to_company):
                completed += 1
                company = future_to_company[future]
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                except Exception as e:
                    # Log error but continue
                    pass
                
                # Progress indicator every 50 companies
                if completed % 50 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    print(f"  ⏱️  Progress: {completed}/{len(COMPANIES)} companies ({elapsed:.1f}s)")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n📊 Total jobs found: {len(all_jobs)} in {elapsed:.1f} seconds")
        return all_jobs
