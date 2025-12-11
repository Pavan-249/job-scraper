"""
High-speed job scraper with parallel execution for 30-second completion
"""
import feedparser
from typing import List, Dict, Any, Optional
import hashlib
from urllib.parse import quote
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import SEARCH_KEYWORDS, REQUIRED_SKILLS, LOCATION, YEAR, SEASON, COMPANIES, MAX_JOB_AGE_HOURS

class JobScraper:
    def __init__(self, max_workers=50):
        self.base_url = "https://www.indeed.com/rss"
        self.max_age_hours = MAX_JOB_AGE_HOURS
        self.max_workers = max_workers  # Parallel workers for speed
    
    def _parse_published_date(self, date_str: str) -> Optional[datetime]:
        """Parse published date from various formats"""
        if not date_str:
            return None
        try:
            return parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return None
    
    def _is_recent_job(self, published_date: Optional[datetime]) -> bool:
        """Check if job was posted recently (within max_age_hours)"""
        if not published_date:
            return True  # Include if we can't determine date
        
        now = datetime.now(published_date.tzinfo) if published_date.tzinfo else datetime.now()
        age = now - published_date
        age_hours = age.total_seconds() / 3600
        
        return age_hours <= self.max_age_hours
    
    def _generate_job_id(self, title: str, company: str, url: str) -> str:
        """Generate unique ID for a job"""
        combined = f"{title}|{company}|{url}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _matches_criteria(self, job: Dict[str, Any]) -> bool:
        """Check if job matches all criteria - optimized for speed"""
        title_lower = job.get('title', '').lower()
        description_lower = job.get('description', '').lower()
        
        # Quick checks first
        if 'intern' not in title_lower:
            return False
        
        # Check keywords
        if not any(keyword.lower() in title_lower or keyword.lower() in description_lower 
                  for keyword in SEARCH_KEYWORDS):
            return False
        
        # Check required skills (Python and SQL)
        if 'python' not in description_lower or 'sql' not in description_lower:
            return False
        
        return True
    
    def search_indeed_rss(self, company: str, keyword: str) -> List[Dict[str, Any]]:
        """Search Indeed RSS feed for jobs - optimized and fast"""
        jobs = []
        try:
            query = f"{keyword} {company}"
            rss_url = f"{self.base_url}?q={quote(query)}&l={quote(LOCATION)}&sort=date&fromage=1"
            
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                for entry in feed.entries[:10]:  # Only check first 10 (most recent)
                    # Parse published date
                    published_str = entry.get('published', '')
                    published_date = self._parse_published_date(published_str)
                    
                    # Skip jobs older than max_age_hours
                    if not self._is_recent_job(published_date):
                        continue
                    
                    # Use summary from RSS - don't fetch full page (too slow!)
                    description = entry.get('summary', '').lower()
                    
                    job = {
                        'id': self._generate_job_id(entry.title, company, entry.get('link', '')),
                        'title': entry.title,
                        'company': company,
                        'location': entry.get('where', LOCATION),
                        'url': entry.get('link', ''),
                        'description': description,
                        'published': published_str,
                        'published_date': published_date.isoformat() if published_date else None
                    }
                    
                    # Filter jobs based on criteria
                    if self._matches_criteria(job):
                        jobs.append(job)
        
        except Exception:
            pass  # Silently skip errors for speed
        
        return jobs
    
    def _search_single_combination(self, company_keyword_tuple) -> List[Dict[str, Any]]:
        """Search single company+keyword combination (for parallel execution)"""
        company, keyword = company_keyword_tuple
        if not company.strip():
            return []
        return self.search_indeed_rss(company, keyword)
    
    def scrape_all_jobs(self) -> List[Dict[str, Any]]:
        """Scrape jobs from all companies and keywords - PARALLEL EXECUTION"""
        print(f"\n🚀 Starting FAST parallel job search across {len(COMPANIES)} companies...")
        print(f"📋 Keywords: {', '.join(SEARCH_KEYWORDS)}")
        print(f"🔧 Required skills: {', '.join(REQUIRED_SKILLS)}")
        print(f"📍 Location: {LOCATION}")
        print(f"📅 Looking for: {SEASON} {YEAR} internships")
        print(f"⏰ Only showing jobs posted in the last {self.max_age_hours} hours")
        print(f"⚡ Using {self.max_workers} parallel workers for speed...\n")
        
        # Create all combinations
        combinations = [(company, keyword) for company in COMPANIES for keyword in SEARCH_KEYWORDS]
        
        all_jobs = []
        start_time = datetime.now()
        
        # Execute in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_combo = {executor.submit(self._search_single_combination, combo): combo 
                              for combo in combinations}
            
            completed = 0
            for future in as_completed(future_to_combo):
                completed += 1
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                    if jobs:
                        for job in jobs:
                            print(f"  ✅ {job['title']} at {job['company']}")
                except Exception:
                    pass
                
                # Progress indicator every 100 searches
                if completed % 100 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    print(f"  ⏱️  Progress: {completed}/{len(combinations)} searches ({elapsed:.1f}s)")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n📊 Total jobs found: {len(all_jobs)} in {elapsed:.1f} seconds")
        return all_jobs
