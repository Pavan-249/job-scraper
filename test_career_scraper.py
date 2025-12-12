"""
Test script to verify career page scraper works with Amazon and Lyft
"""
from company_career_scraper import CompanyCareerScraper
from career_page_finder import CareerPageFinder

def test_amazon():
    """Test Amazon career page scraping"""
    print("\n" + "="*60)
    print("Testing Amazon Career Page Scraper")
    print("="*60)
    
    scraper = CompanyCareerScraper()
    jobs = scraper.scrape_company_internships("Amazon")
    
    print(f"\nFound {len(jobs)} internship(s) at Amazon:")
    for job in jobs:
        print(f"\n  Title: {job['title']}")
        print(f"  URL: {job['url']}")
        print(f"  Location: {job['location']}")
        print(f"  Description preview: {job['description'][:200]}...")
    
    return jobs

def test_lyft():
    """Test Lyft career page scraping"""
    print("\n" + "="*60)
    print("Testing Lyft Career Page Scraper")
    print("="*60)
    
    scraper = CompanyCareerScraper()
    jobs = scraper.scrape_company_internships("Lyft")
    
    print(f"\nFound {len(jobs)} internship(s) at Lyft:")
    for job in jobs:
        print(f"\n  Title: {job['title']}")
        print(f"  URL: {job['url']}")
        print(f"  Location: {job['location']}")
        print(f"  Description preview: {job['description'][:200]}...")
    
    return jobs

def test_career_page_finder():
    """Test career page finder"""
    print("\n" + "="*60)
    print("Testing Career Page Finder")
    print("="*60)
    
    finder = CareerPageFinder()
    
    test_companies = ["Amazon", "Lyft", "Google", "Microsoft", "Meta"]
    
    for company in test_companies:
        info = finder.get_career_page_info(company)
        print(f"\n{company}:")
        print(f"  URL: {info['url']}")
        print(f"  ATS Type: {info['ats_type']}")
        print(f"  Verified: {info['verified']}")

if __name__ == "__main__":
    # Test career page finder first
    test_career_page_finder()
    
    # Test Amazon
    amazon_jobs = test_amazon()
    
    # Test Lyft
    lyft_jobs = test_lyft()
    
    print("\n" + "="*60)
    print(f"Summary: Found {len(amazon_jobs)} Amazon jobs and {len(lyft_jobs)} Lyft jobs")
    print("="*60)

