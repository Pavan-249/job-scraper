"""
Career page finder - identifies and verifies company career pages
Supports common patterns and ATS systems
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import re
from urllib.parse import urljoin, urlparse
import time

class CareerPageFinder:
    """Finds and verifies company career pages"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.timeout = 10
        
        # Common career page patterns
        self.career_patterns = [
            '/careers',
            '/jobs',
            '/careers/jobs',
            '/career',
            '/job',
            '/hiring',
            '/opportunities',
            '/work-with-us',
            '/join-us',
            '/open-positions',
            '/current-openings',
        ]
        
        # Known ATS systems and their URL patterns
        self.ats_patterns = {
            'greenhouse': ['greenhouse.io', 'boards.greenhouse.io'],
            'lever': ['lever.co', 'jobs.lever.co'],
            'workday': ['myworkdayjobs.com', 'wd*.myworkdayjobs.com'],
            'smartrecruiters': ['smartrecruiters.com'],
            'icims': ['icims.com'],
            'taleo': ['taleo.net'],
            'jobvite': ['jobvite.com'],
        }
        
        # Company-specific career page mappings (known patterns)
        self.company_mappings = {
            'Amazon': 'https://www.amazon.jobs',
            'Google': 'https://careers.google.com',
            'Microsoft': 'https://careers.microsoft.com',
            'Meta': 'https://www.metacareers.com',
            'Apple': 'https://jobs.apple.com',
            'Netflix': 'https://jobs.netflix.com',
            'Tesla': 'https://www.tesla.com/careers',
            'Nvidia': 'https://nvidia.wd5.myworkdayjobs.com',
            'Oracle': 'https://careers.oracle.com',
            'IBM': 'https://www.ibm.com/careers',
            'Salesforce': 'https://www.salesforce.com/careers',
            'Adobe': 'https://careers.adobe.com',
            'Lyft': 'https://www.lyft.com/careers',
            'Uber': 'https://www.uber.com/careers',
            'Stripe': 'https://stripe.com/jobs',
            'Palantir': 'https://www.palantir.com/careers',
            'Snowflake': 'https://careers.snowflake.com',
            'Databricks': 'https://www.databricks.com/company/careers',
            'Facebook': 'https://www.metacareers.com',
        }
    
    def normalize_company_name(self, company: str) -> str:
        """Normalize company name for URL generation"""
        # Remove common suffixes
        company = company.replace(' Inc.', '').replace(' Inc', '')
        company = company.replace(' LLC', '').replace(' Ltd.', '').replace(' Ltd', '')
        company = company.replace(' Corp.', '').replace(' Corporation', '')
        
        # Convert to lowercase for URL
        return company.lower().strip()
    
    def find_career_page(self, company: str) -> Optional[str]:
        """
        Find career page for a company
        Returns the career page URL if found, None otherwise
        """
        # Check known mappings first
        if company in self.company_mappings:
            url = self.company_mappings[company]
            if self._verify_career_page(url):
                return url
        
        # Try common domain patterns
        base_domains = self._generate_base_domains(company)
        
        for base_domain in base_domains:
            # Try direct career page patterns
            for pattern in self.career_patterns:
                test_url = f"{base_domain}{pattern}"
                if self._verify_career_page(test_url):
                    return test_url
            
            # Try to find career link on homepage
            career_url = self._find_career_link_on_homepage(base_domain)
            if career_url:
                return career_url
        
        return None
    
    def _generate_base_domains(self, company: str) -> List[str]:
        """Generate possible base domains for a company"""
        normalized = self.normalize_company_name(company)
        
        # Common domain patterns
        domains = [
            f"https://www.{normalized}.com",
            f"https://{normalized}.com",
            f"https://www.{normalized}.io",
            f"https://{normalized}.io",
            f"https://www.{normalized}.co",
            f"https://{normalized}.co",
        ]
        
        # Handle special cases
        special_cases = {
            'meta': 'https://www.meta.com',
            'facebook': 'https://www.meta.com',
            'google': 'https://careers.google.com',
            'microsoft': 'https://careers.microsoft.com',
            'amazon': 'https://www.amazon.jobs',
        }
        
        if normalized in special_cases:
            domains.insert(0, special_cases[normalized])
        
        return domains
    
    def _verify_career_page(self, url: str) -> bool:
        """Verify if a URL is a valid career page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            if response.status_code != 200:
                return False
            
            # Check for career-related keywords in content
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text().lower()
            
            # Career page indicators
            career_indicators = [
                'job', 'career', 'open position', 'hiring', 'opportunity',
                'apply', 'internship', 'intern', 'full-time', 'part-time'
            ]
            
            # Check if page contains career-related content
            indicator_count = sum(1 for indicator in career_indicators if indicator in text)
            
            # Also check for common ATS systems
            page_url = response.url.lower()
            for ats_name, patterns in self.ats_patterns.items():
                if any(pattern in page_url for pattern in patterns):
                    return True
            
            # If we have enough indicators, it's likely a career page
            return indicator_count >= 3
            
        except Exception as e:
            return False
    
    def _find_career_link_on_homepage(self, base_url: str) -> Optional[str]:
        """Find career page link on company homepage"""
        try:
            response = requests.get(base_url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for links containing career-related keywords
            career_keywords = ['career', 'job', 'hiring', 'opportunity', 'work with us', 'join us']
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                for keyword in career_keywords:
                    if keyword in href or keyword in text:
                        full_url = urljoin(base_url, link['href'])
                        if self._verify_career_page(full_url):
                            return full_url
            
            return None
            
        except Exception:
            return None
    
    def get_career_page_info(self, company: str) -> Dict[str, any]:
        """Get career page information including ATS type"""
        career_url = self.find_career_page(company)
        
        if not career_url:
            return {'url': None, 'ats_type': None, 'verified': False}
        
        # Detect ATS type
        ats_type = self._detect_ats_type(career_url)
        
        return {
            'url': career_url,
            'ats_type': ats_type,
            'verified': True
        }
    
    def _detect_ats_type(self, url: str) -> Optional[str]:
        """Detect which ATS system is being used"""
        url_lower = url.lower()
        
        for ats_name, patterns in self.ats_patterns.items():
            if any(pattern in url_lower for pattern in patterns):
                return ats_name
        
        # Check for other indicators
        if 'workday' in url_lower:
            return 'workday'
        elif 'greenhouse' in url_lower:
            return 'greenhouse'
        elif 'lever' in url_lower:
            return 'lever'
        
        return 'custom'

