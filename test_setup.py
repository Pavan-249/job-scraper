"""
Quick test script to verify setup is correct
"""
import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing imports...")
    try:
        import requests
        import bs4
        import feedparser
        import schedule
        import dotenv
        print("✅ All packages imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def test_config():
    """Test if config file exists and is readable"""
    print("\n🔍 Testing config...")
    try:
        from config import COMPANIES, SEARCH_KEYWORDS, REQUIRED_SKILLS
        print(f"✅ Config loaded successfully!")
        print(f"   Companies: {len(COMPANIES)}")
        print(f"   Keywords: {', '.join(SEARCH_KEYWORDS)}")
        print(f"   Required skills: {', '.join(REQUIRED_SKILLS)}")
        if len(COMPANIES) < 5:
            print("   ⚠️  Warning: You have fewer than 5 companies. Add more to config.py")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_env():
    """Test if .env file exists"""
    print("\n🔍 Testing .env file...")
    if os.path.exists('.env'):
        print("✅ .env file exists!")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            email_sender = os.getenv("EMAIL_SENDER")
            email_password = os.getenv("EMAIL_PASSWORD")
            email_recipient = os.getenv("EMAIL_RECIPIENT")
            
            if email_sender and email_password and email_recipient:
                print("✅ Email configuration found!")
                return True
            else:
                print("⚠️  Email configuration incomplete in .env")
                print("   Make sure EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECIPIENT are set")
                return False
        except Exception as e:
            print(f"⚠️  Could not load .env: {e}")
            return False
    else:
        print("⚠️  .env file not found!")
        print("   Create it by copying .env.example:")
        print("   cp .env.example .env")
        print("   Then edit .env with your email settings")
        return False

def main():
    print("="*60)
    print("🧪 Testing Job Scraper Setup")
    print("="*60)
    
    results = []
    results.append(test_imports())
    results.append(test_config())
    results.append(test_env())
    
    print("\n" + "="*60)
    if all(results):
        print("✅ All tests passed! You're ready to run the scraper!")
        print("\nRun: python3 main.py --run-once")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    print("="*60)

if __name__ == "__main__":
    main()

