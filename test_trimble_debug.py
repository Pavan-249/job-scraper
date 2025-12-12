"""
Debug script to see what Trimble jobs are actually available
"""
import feedparser
from urllib.parse import quote

def test_trimble_rss():
    """Test raw RSS feed for Trimble"""
    print("="*60)
    print("🔍 Debug: Testing Trimble RSS Feed")
    print("="*60 + "\n")
    
    # Test different search queries
    queries = [
        "data analyst intern Trimble",
        "data engineer intern Trimble",
        "intern Trimble",
        "Trimble intern"
    ]
    
    location = "United States"
    base_url = "https://www.indeed.com/rss"
    
    for query in queries:
        print(f"\n📋 Testing query: '{query}'")
        rss_url = f"{base_url}?q={quote(query)}&l={quote(location)}&sort=date&fromage=2"
        print(f"🔗 URL: {rss_url}\n")
        
        try:
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                print(f"  ✅ Found {len(feed.entries)} job(s):")
                for i, entry in enumerate(feed.entries[:5], 1):  # Show first 5
                    title = entry.get('title', 'N/A')
                    published = entry.get('published', 'N/A')
                    link = entry.get('link', 'N/A')
                    summary = entry.get('summary', '')[:200]  # First 200 chars
                    
                    print(f"\n  {i}. {title}")
                    print(f"     📅 Published: {published}")
                    print(f"     🔗 Link: {link}")
                    print(f"     📄 Summary: {summary}...")
                    
                    # Check for Python and SQL
                    summary_lower = summary.lower()
                    has_python = 'python' in summary_lower
                    has_sql = 'sql' in summary_lower
                    has_intern = 'intern' in title.lower()
                    
                    print(f"     ✓ Has 'intern': {has_intern}")
                    print(f"     ✓ Has 'python': {has_python}")
                    print(f"     ✓ Has 'sql': {has_sql}")
            else:
                print(f"  ⚠️  No jobs found")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_trimble_rss()




