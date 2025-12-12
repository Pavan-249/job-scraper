"""
Company career page scraper - scrapes internships from company career pages
Supports multiple ATS systems and custom pages
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Tuple
import re
import json
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime, timedelta
import hashlib
from career_page_finder import CareerPageFinder
import time
from email.utils import parsedate_to_datetime
from config import MAX_JOB_AGE_HOURS, MAX_JOB_AGE_HOURS_FALLBACK

class CompanyCareerScraper:
    """Scrapes internships from company career pages"""
    
    def __init__(self):
        self.finder = CareerPageFinder()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.timeout = 8  # Reduced timeout for speed
        
        # Keywords to search for in job listings
        self.intern_keywords = ['intern', 'internship', 'co-op', 'coop']
        
        # Phrases that indicate it's NOT an internship (false positives)
        self.not_intern_phrases = [
            'internal controls', 'internal audit', 'internal review',
            'internal process', 'internal system', 'internal tool',
            'internal team', 'internal communication'
        ]
        
        # Cloud intern indicators (from user's example)
        self.cloud_intern_indicators = [
            'minimum of one quarter/semester/trimester remaining',
            'aws support team', 'cloud support', 'cloud computing',
            'aws professional services', 'cloud technology',
            'troubleshooting labs', 'simulated customer cases',
            'certification attainment', 'experiential learning'
        ]
        
        # Data-related keywords (for intelligent matching)
        self.data_keywords = [
            'data analyst', 'data engineer', 'data architect', 'data scientist',
            'analytics', 'business intelligence', 'bi', 'etl', 'data pipeline',
            'data warehouse', 'data lake', 'machine learning', 'ml', 'ai',
            'distributed systems', 'genai', 'observability', 'data infrastructure',
            'data platform', 'data quality', 'data governance'
        ]
        
        # Technical skills that indicate data roles
        self.data_skills = [
            'python', 'sql', 'spark', 'hadoop', 'kafka', 'airflow', 'dbt',
            'snowflake', 'databricks', 'redshift', 'bigquery', 'tableau',
            'power bi', 'looker', 'pandas', 'numpy', 'scikit-learn', 'tensorflow',
            'pytorch', 'r', 'scala', 'java', 'go', 'c++', 'distributed systems',
            'genai', 'llm', 'opentelemetry', 'observability'
        ]
    
    def scrape_company_internships(self, company: str) -> List[Dict[str, Any]]:
        """Scrape all internships from a company's career page"""
        # Get career page info
        career_info = self.finder.get_career_page_info(company)
        
        if not career_info['verified'] or not career_info['url']:
            return []
        
        career_url = career_info['url']
        ats_type = career_info['ats_type']
        
        # Route to appropriate scraper based on ATS type
        jobs = []
        if ats_type == 'greenhouse':
            jobs = self._scrape_greenhouse(career_url, company)
        elif ats_type == 'lever':
            jobs = self._scrape_lever(career_url, company)
        elif ats_type == 'workday':
            jobs = self._scrape_workday(career_url, company)
        elif 'amazon.jobs' in career_url.lower():
            jobs = self._scrape_amazon(career_url, company)
        elif 'lyft.com' in career_url.lower():
            jobs = self._scrape_lyft(career_url, company)
        else:
            # Try generic scraper
            jobs = self._scrape_generic(career_url, company)
        
        # Final filtering: verify internships and check dates
        filtered_jobs = []
        for job in jobs:
            # Verify it's actually an internship
            if not self._verify_actual_internship(job):
                continue
            
            # Check if data-related
            if not self._is_data_related_internship(job):
                continue
            
            # Check if recent (already done in fetch methods, but double-check)
            if not self._is_recent_job(job):
                continue
            
            filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _scrape_amazon(self, url: str, company: str) -> List[Dict[str, Any]]:
        """Scrape Amazon jobs page"""
        jobs = []
        try:
            # Amazon uses a specific structure
            # Try the internships page directly (user provided this URL)
            intern_urls = [
                f"{url}/content/en/career-programs/university/internships-for-students?country%5B%5D=US",
                f"{url}/en/search?base_query=intern&loc_query=United%20States",
                f"{url}/en/search?base_query=internship&loc_query=United%20States",
                f"{url}/en/search?base_query=data+intern&loc_query=United%20States",
            ]
            
            for intern_url in intern_urls:
                try:
                    response = requests.get(intern_url, headers=self.headers, timeout=self.timeout)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Check if page has content (might be JS-rendered)
                        page_text = soup.get_text()
                        if len(page_text) < 500:
                            # Page might be JS-rendered, try to find JSON data
                            scripts = soup.find_all('script')
                            for script in scripts:
                                script_text = script.string or ""
                                if 'job' in script_text.lower() or 'position' in script_text.lower():
                                    # Try to extract job data from script
                                    jobs.extend(self._extract_jobs_from_script(script_text, company, intern_url))
                            continue
                        
                        # Amazon may use different structures - try multiple approaches
                        # Approach 1: Look for job cards/containers with various class patterns
                        job_cards = soup.find_all(['div', 'article', 'li', 'section', 'tr'], 
                                                 class_=re.compile(r'job|position|opening|card|listing|result|row|item', re.I))
                        
                        for card in job_cards:
                            job = self._parse_amazon_job(card, company, intern_url)
                            if job and self._is_data_related_internship(job):
                                # Avoid duplicates
                                if not any(j['url'] == job['url'] for j in jobs):
                                    jobs.append(job)
                        
                        # Approach 2: Find all links that might be jobs (more aggressive)
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            # Check if it looks like a job link
                            if any(keyword in text.lower() for keyword in self.intern_keywords) or \
                               '/job/' in href.lower() or '/jobs/' in href.lower() or \
                               'jobid' in href.lower():
                                if href.startswith('http') or href.startswith('/'):
                                    full_url = urljoin(intern_url, href)
                                    job = self._fetch_amazon_job_detail(full_url, company)
                                    if job and self._is_data_related_internship(job):
                                        # Avoid duplicates
                                        if not any(j['url'] == job['url'] for j in jobs):
                                            jobs.append(job)
                        
                        # Approach 3: Look for data attributes or specific Amazon structures
                        job_elements = soup.find_all(attrs={'data-job-id': True})
                        for elem in job_elements:
                            job = self._parse_amazon_job(elem, company, intern_url)
                            if job and self._is_data_related_internship(job):
                                if not any(j['url'] == job['url'] for j in jobs):
                                    jobs.append(job)
                        
                        # Approach 4: Look for any element with job-related text
                        all_elements = soup.find_all(['div', 'span', 'p', 'a'])
                        for elem in all_elements:
                            text = elem.get_text(strip=True)
                            if text and any(keyword in text.lower() for keyword in self.intern_keywords):
                                # Check if it's a link or has a link nearby
                                link = elem.find('a', href=True) if elem.name != 'a' else elem
                                if link and link.get('href'):
                                    href = link.get('href')
                                    if '/job/' in href.lower() or '/jobs/' in href.lower():
                                        full_url = urljoin(intern_url, href)
                                        job = self._fetch_amazon_job_detail(full_url, company)
                                        if job and self._is_data_related_internship(job):
                                            if not any(j['url'] == job['url'] for j in jobs):
                                                jobs.append(job)
                except Exception as e:
                    continue
                    
        except Exception as e:
            pass
        
        return jobs
    
    def _extract_jobs_from_script(self, script_text: str, company: str, base_url: str) -> List[Dict[str, Any]]:
        """Try to extract job data from JavaScript/JSON in script tags"""
        jobs = []
        try:
            # Look for JSON-like structures
            import json
            import re
            
            # Try to find JSON objects
            json_pattern = r'\{[^{}]*"job"[^{}]*\}'
            matches = re.findall(json_pattern, script_text, re.IGNORECASE)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    # Process if it looks like job data
                    if 'title' in data or 'jobTitle' in data:
                        title = data.get('title') or data.get('jobTitle', '')
                        if self._is_internship(title):
                            job_url = data.get('url') or data.get('link', '')
                            if job_url:
                                job = self._fetch_amazon_job_detail(urljoin(base_url, job_url), company)
                                if job and self._is_data_related_internship(job):
                                    jobs.append(job)
                except:
                    continue
        except Exception:
            pass
        return jobs
    
    def _parse_amazon_job(self, card, company: str, base_url: str) -> Optional[Dict[str, Any]]:
        """Parse an Amazon job card"""
        try:
            # Find title
            title_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|heading', re.I))
            if not title_elem:
                title_elem = card.find(['h2', 'h3', 'h4', 'a'])
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            # Check if it's an internship
            if not any(keyword in title.lower() for keyword in self.intern_keywords):
                return None
            
            # Find link
            link_elem = card.find('a', href=True) or title_elem.find('a', href=True) if title_elem.name != 'a' else title_elem
            if not link_elem or not link_elem.get('href'):
                return None
            
            job_url = urljoin(base_url, link_elem['href'])
            
            # Try to get description from card
            desc_elem = card.find(['div', 'p'], class_=re.compile(r'description|summary|detail', re.I))
            description = desc_elem.get_text() if desc_elem else ""
            published_date = None
            
            # Fetch full description if needed
            if not description or len(description) < 100:
                full_desc, date, _ = self._fetch_job_description(job_url)
                if full_desc:
                    description = full_desc
                    published_date = date
            
            job = {
                'id': self._generate_job_id(title, company, job_url),
                'title': title,
                'company': company,
                'location': self._extract_location(card),
                'url': job_url,
                'description': description,
                'published': '',
                'published_date': published_date.isoformat() if published_date else None
            }
            
            # Check if recent before returning
            if not self._is_recent_job(job):
                return None
            
            return job
        except Exception:
            return None
    
    def _fetch_amazon_job_detail(self, url: str, company: str) -> Optional[Dict[str, Any]]:
        """Fetch full job details from Amazon job page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find title
                title_elem = soup.find(['h1', 'h2'], class_=re.compile(r'title|heading', re.I))
                if not title_elem:
                    title_elem = soup.find('h1')
                
                if not title_elem:
                    return None
                
                title = title_elem.get_text(strip=True)
                
                # Get description
                desc_elem = soup.find(['div', 'section'], class_=re.compile(r'description|content|detail', re.I))
                description = desc_elem.get_text() if desc_elem else ""
                
                # Verify it's actually an internship (not just in URL)
                temp_job = {'title': title, 'description': description}
                if not self._verify_actual_internship(temp_job):
                    return None
                
                # Parse date
                published_date = self._parse_job_date(soup, url)
                
                # Check if recent
                job = {
                    'id': self._generate_job_id(title, company, url),
                    'title': title,
                    'company': company,
                    'location': self._extract_location_from_soup(soup),
                    'url': url,
                    'description': description,
                    'published': '',
                    'published_date': published_date.isoformat() if published_date else None
                }
                
                if not self._is_recent_job(job, response.headers):
                    return None
                
                return job
        except Exception:
            return None
    
    def _extract_location_from_soup(self, soup: BeautifulSoup) -> str:
        """Extract location from soup"""
        try:
            location_elem = soup.find(['div', 'span'], class_=re.compile(r'location', re.I))
            if location_elem:
                return location_elem.get_text(strip=True)
            
            # Try job details section
            job_details = soup.find(['div', 'section'], class_=re.compile(r'job.*detail|detail', re.I))
            if job_details:
                location_elem = job_details.find(string=re.compile(r'USA|United States|US,', re.I))
                if location_elem:
                    return location_elem.strip()
        except Exception:
            pass
        return "United States"
    
    def _scrape_greenhouse(self, url: str, company: str) -> List[Dict[str, Any]]:
        """Scrape Greenhouse ATS"""
        jobs = []
        try:
            # Greenhouse API endpoint
            api_url = url.replace('/jobs', '/jobs.json') if '/jobs' in url else f"{url}/jobs.json"
            
            response = requests.get(api_url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                
                for job in data.get('jobs', []):
                    if self._is_internship(job.get('title', '')):
                        full_job = self._fetch_greenhouse_job(job.get('absolute_url', ''), company)
                        if full_job and self._is_data_related_internship(full_job):
                            jobs.append(full_job)
        except Exception:
            # Fallback to HTML scraping
            return self._scrape_generic(url, company)
        
        return jobs
    
    def _fetch_greenhouse_job(self, url: str, company: str) -> Optional[Dict[str, Any]]:
        """Fetch individual Greenhouse job"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title_elem = soup.find('h1', {'id': 'header'})
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                desc_elem = soup.find('div', {'id': 'content'})
                description = desc_elem.get_text() if desc_elem else ""
                
                location_elem = soup.find('div', class_='location')
                location = location_elem.get_text(strip=True) if location_elem else "United States"
                
                return {
                    'id': self._generate_job_id(title, company, url),
                    'title': title,
                    'company': company,
                    'location': location,
                    'url': url,
                    'description': description,
                    'published': '',
                    'published_date': None
                }
        except Exception:
            return None
    
    def _scrape_lever(self, url: str, company: str) -> List[Dict[str, Any]]:
        """Scrape Lever ATS"""
        jobs = []
        try:
            # Lever API
            api_url = url.rstrip('/') + '/api/v0/postings'
            
            response = requests.get(api_url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                
                for job in data:
                    if self._is_internship(job.get('text', '')):
                        job_url = job.get('hostedUrl', '') or job.get('applyUrl', '')
                        if job_url:
                            full_job = self._fetch_lever_job(job_url, company, job)
                            if full_job and self._is_data_related_internship(full_job):
                                jobs.append(full_job)
        except Exception:
            return self._scrape_generic(url, company)
        
        return jobs
    
    def _fetch_lever_job(self, url: str, company: str, job_data: Dict) -> Optional[Dict[str, Any]]:
        """Fetch individual Lever job"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title = job_data.get('text', '')
                desc_elem = soup.find('div', class_='content')
                description = desc_elem.get_text() if desc_elem else ""
                
                location = job_data.get('categories', {}).get('location', 'United States')
                
                return {
                    'id': self._generate_job_id(title, company, url),
                    'title': title,
                    'company': company,
                    'location': location,
                    'url': url,
                    'description': description,
                    'published': '',
                    'published_date': None
                }
        except Exception:
            return None
    
    def _scrape_workday(self, url: str, company: str) -> List[Dict[str, Any]]:
        """Scrape Workday ATS"""
        # Workday is complex, use generic scraper
        return self._scrape_generic(url, company)
    
    def _scrape_lyft(self, url: str, company: str) -> List[Dict[str, Any]]:
        """Scrape Lyft career page"""
        jobs = []
        try:
            # Try different Lyft career page URLs
            intern_urls = [
                f"{url}/early-careers",
                f"{url}/university",
                f"{url}?q=intern",
                f"{url}?q=internship",
            ]
            
            for intern_url in intern_urls:
                try:
                    response = requests.get(intern_url, headers=self.headers, timeout=self.timeout)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for job listings
                        job_cards = soup.find_all(['div', 'article', 'li', 'section'], 
                                                 class_=re.compile(r'job|position|opening|card|listing|result|posting', re.I))
                        
                        for card in job_cards:
                            job = self._parse_generic_job_card(card, company, intern_url)
                            if job and self._is_data_related_internship(job):
                                if not any(j['url'] == job['url'] for j in jobs):
                                    jobs.append(job)
                        
                        # Also look for links
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            if any(keyword in text.lower() for keyword in self.intern_keywords) or \
                               '/job/' in href.lower() or '/jobs/' in href.lower() or \
                               '/careers/' in href.lower():
                                if href.startswith('http') or href.startswith('/'):
                                    full_url = urljoin(intern_url, href)
                                    job = self._fetch_job_from_url(full_url, company, text)
                                    if job and self._is_data_related_internship(job):
                                        if not any(j['url'] == job['url'] for j in jobs):
                                            jobs.append(job)
                except Exception:
                    continue
        except Exception:
            pass
        
        return jobs
    
    def _scrape_generic(self, url: str, company: str) -> List[Dict[str, Any]]:
        """Generic scraper for unknown ATS systems"""
        jobs = []
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all links that might be jobs
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Check if it looks like a job link
                    if any(keyword in text.lower() for keyword in self.intern_keywords):
                        if href.startswith('http') or href.startswith('/'):
                            job_url = urljoin(url, href)
                            job = self._fetch_job_from_url(job_url, company, text)
                            if job and self._is_data_related_internship(job):
                                # Avoid duplicates
                                if not any(j['url'] == job['url'] for j in jobs):
                                    jobs.append(job)
                
                # Also look for job cards/divs
                job_containers = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'job|position|opening|card|listing', re.I))
                
                for container in job_containers:
                    job = self._parse_generic_job_card(container, company, url)
                    if job and self._is_data_related_internship(job):
                        if not any(j['url'] == job['url'] for j in jobs):
                            jobs.append(job)
        except Exception:
            pass
        
        return jobs
    
    def _parse_generic_job_card(self, card, company: str, base_url: str) -> Optional[Dict[str, Any]]:
        """Parse a generic job card"""
        try:
            # Find title
            title_elem = card.find(['h2', 'h3', 'h4', 'a', 'span'], class_=re.compile(r'title|heading|name', re.I))
            if not title_elem:
                title_elem = card.find(['h2', 'h3', 'h4'])
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            if not self._is_internship(title):
                return None
            
            # Find link
            link_elem = card.find('a', href=True) or (title_elem if title_elem.name == 'a' else title_elem.find('a', href=True))
            if not link_elem or not link_elem.get('href'):
                return None
            
            job_url = urljoin(base_url, link_elem['href'])
            
            # Get description
            desc_elem = card.find(['div', 'p'], class_=re.compile(r'description|summary|detail', re.I))
            description = desc_elem.get_text() if desc_elem else ""
            published_date = None
            
            # Fetch full description
            if not description or len(description) < 100:
                full_desc, date, _ = self._fetch_job_description(job_url)
                if full_desc:
                    description = full_desc
                    published_date = date
            
            job = {
                'id': self._generate_job_id(title, company, job_url),
                'title': title,
                'company': company,
                'location': self._extract_location(card),
                'url': job_url,
                'description': description,
                'published': '',
                'published_date': published_date.isoformat() if published_date else None
            }
            
            # Check if recent before returning
            if not self._is_recent_job(job):
                return None
            
            return job
        except Exception:
            return None
    
    def _fetch_job_from_url(self, url: str, company: str, title: str) -> Optional[Dict[str, Any]]:
        """Fetch job details from a URL"""
        try:
            description, published_date, headers = self._fetch_job_description(url)
            if description:
                job = {
                    'id': self._generate_job_id(title, company, url),
                    'title': title,
                    'company': company,
                    'location': 'United States',
                    'url': url,
                    'description': description,
                    'published': '',
                    'published_date': published_date.isoformat() if published_date else None
                }
                
                # Check if recent
                if not self._is_recent_job(job, headers):
                    return None
                
                return job
        except Exception:
            pass
        return None
    
    def _fetch_job_description(self, url: str) -> Tuple[str, Optional[datetime], Dict]:
        """Fetch full job description from URL, returns (description, date, headers)"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try common description selectors
                desc_selectors = [
                    {'id': 'jobDescriptionText'},
                    {'class': 'job-description'},
                    {'class': 'description'},
                    {'class': 'job-details'},
                    {'class': 'content'},
                ]
                
                description = ""
                for selector in desc_selectors:
                    desc_elem = soup.find('div', selector)
                    if desc_elem:
                        description = desc_elem.get_text()
                        break
                
                if not description:
                    # Fallback: get all text
                    description = soup.get_text()
                
                # Parse date
                published_date = self._parse_job_date(soup, url)
                
                return description, published_date, response.headers
        except Exception:
            pass
        return "", None, {}
    
    def _is_internship(self, text: str) -> bool:
        """Check if text indicates an internship (with false positive filtering)"""
        text_lower = text.lower()
        
        # First check: must have intern keyword
        if not any(keyword in text_lower for keyword in self.intern_keywords):
            return False
        
        # Second check: exclude false positives
        for phrase in self.not_intern_phrases:
            if phrase in text_lower:
                return False
        
        return True
    
    def _verify_actual_internship(self, job: Dict[str, Any]) -> bool:
        """Verify that this is actually an internship position by checking description"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        combined = f"{title} {description}"
        
        # Must have intern keyword
        if not any(keyword in combined for keyword in self.intern_keywords):
            return False
        
        # Exclude false positives
        for phrase in self.not_intern_phrases:
            if phrase in combined:
                return False
        
        # Verify with internship indicators in description
        internship_indicators = [
            'internship', 'intern', 'co-op', 'coop',
            'quarter/semester/trimester remaining',
            'enrolled in', 'student', 'university program',
            'summer intern', 'winter intern', 'spring intern',
            'intern program', 'internship program'
        ]
        
        # If title has intern but description doesn't confirm, be cautious
        if any(keyword in title for keyword in self.intern_keywords):
            # Description should have some confirmation
            if len(description) > 100:  # Has substantial description
                if not any(indicator in combined for indicator in internship_indicators):
                    # Might be false positive, skip
                    return False
        
        return True
    
    def _is_data_related_internship(self, job: Dict[str, Any]) -> bool:
        """
        Intelligently determine if an internship is data-related
        Based on user's requirements:
        1. Explicit data roles (data analyst/engineer/architect)
        2. Python + SQL mentioned
        3. Data-related skills even without explicit SQL (e.g., Python + distributed systems/GenAI)
        4. Cloud support/engineering internships with specific patterns
        """
        title_lower = job.get('title', '').lower()
        desc_lower = job.get('description', '').lower()
        combined_text = f"{title_lower} {desc_lower}"
        
        # First verify it's actually an internship
        if not self._verify_actual_internship(job):
            return False
        
        # Check 1: Explicit data role keywords
        if any(keyword in combined_text for keyword in self.data_keywords):
            return True
        
        # Check 2: Cloud intern pattern (from user's example)
        cloud_intern_count = sum(1 for indicator in self.cloud_intern_indicators if indicator in combined_text)
        if cloud_intern_count >= 2:  # At least 2 cloud intern indicators
            # Also check for technical skills
            tech_skills = ['python', 'sql', 'cloud', 'aws', 'azure', 'gcp', 'networking', 'linux', 'database']
            if any(skill in combined_text for skill in tech_skills):
                return True
        
        # Check 3: Python + SQL (explicit requirement)
        has_python = 'python' in combined_text
        has_sql = 'sql' in combined_text
        
        if has_python and has_sql:
            return True
        
        # Check 4: Python + data-related technologies (intelligent matching)
        if has_python:
            # Check for data-related skills/technologies
            data_tech_indicators = [
                'distributed systems', 'genai', 'llm', 'machine learning', 'ml',
                'data pipeline', 'etl', 'data warehouse', 'data lake', 'spark',
                'hadoop', 'kafka', 'airflow', 'observability', 'opentelemetry',
                'analytics', 'business intelligence', 'data infrastructure',
                'data platform', 'data quality', 'data governance', 'snowflake',
                'databricks', 'redshift', 'bigquery', 'tableau', 'power bi'
            ]
            
            if any(indicator in combined_text for indicator in data_tech_indicators):
                return True
        
        # Check 5: Other data skills even without Python
        data_skill_count = sum(1 for skill in self.data_skills if skill in combined_text)
        if data_skill_count >= 2:  # At least 2 data-related skills
            return True
        
        return False
    
    def _parse_job_date(self, soup: BeautifulSoup, url: str) -> Optional[datetime]:
        """Parse job posting date from page"""
        try:
            # Try to find date in various formats
            # Look for date elements
            date_selectors = [
                {'class': re.compile(r'date|posted|published', re.I)},
                {'id': re.compile(r'date|posted|published', re.I)},
            ]
            
            for selector in date_selectors:
                date_elem = soup.find(['div', 'span', 'time'], selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    # Try to parse various date formats
                    date = self._parse_date_string(date_text)
                    if date:
                        return date
            
            # Try to find time element
            time_elem = soup.find('time', datetime=True)
            if time_elem:
                datetime_str = time_elem.get('datetime', '')
                if datetime_str:
                    date = self._parse_date_string(datetime_str)
                    if date:
                        return date
            
            # Check HTTP headers
            # This would require the response object, so we'll handle it in the calling function
            
            return None
        except Exception:
            return None
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats"""
        if not date_str:
            return None
        
        try:
            # Try RFC 2822 format
            return parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    # Try common formats
                    formats = [
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d',
                        '%m/%d/%Y',
                        '%d/%m/%Y',
                        '%B %d, %Y',
                        '%b %d, %Y',
                    ]
                    for fmt in formats:
                        try:
                            return datetime.strptime(date_str.strip(), fmt)
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        return None
    
    def _is_recent_job(self, job: Dict[str, Any], response_headers: Dict = None) -> bool:
        """Check if job was posted recently (within MAX_JOB_AGE_HOURS)"""
        published_date = job.get('published_date')
        
        # If we have a parsed date, use it
        if published_date:
            if isinstance(published_date, str):
                try:
                    published_date = datetime.fromisoformat(published_date)
                except:
                    published_date = None
        
        if published_date:
            now = datetime.now(published_date.tzinfo) if published_date.tzinfo else datetime.now()
            age = now - published_date
            age_hours = age.total_seconds() / 3600
            return age_hours <= MAX_JOB_AGE_HOURS
        
        # If no date available, check HTTP headers
        if response_headers:
            # Check Last-Modified header
            last_modified = response_headers.get('Last-Modified')
            if last_modified:
                try:
                    date = parsedate_to_datetime(last_modified)
                    now = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
                    age = now - date
                    age_hours = age.total_seconds() / 3600
                    return age_hours <= MAX_JOB_AGE_HOURS
                except:
                    pass
        
        # If we can't determine date, use fallback (24 hours) - be conservative
        # User wants only recent jobs, so if we can't verify, exclude it
        return False  # Exclude if we can't verify it's recent
    
    def _extract_location(self, element) -> str:
        """Extract location from job card element"""
        try:
            location_elem = element.find(['div', 'span'], class_=re.compile(r'location', re.I))
            if location_elem:
                return location_elem.get_text(strip=True)
        except Exception:
            pass
        return "United States"
    
    def _generate_job_id(self, title: str, company: str, url: str) -> str:
        """Generate unique ID for a job"""
        combined = f"{title}|{company}|{url}"
        return hashlib.md5(combined.encode()).hexdigest()

