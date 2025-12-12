"""
Test Trimble without date restrictions
"""
import feedparser
from urllib.parse import quote
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_and_send_email():
    """Find ANY Trimble intern job and send test email"""
    print("="*60)
    print("🔍 Testing Trimble - All Time (No Date Filter)")
    print("="*60 + "\n")
    
    queries = [
        "Trimble intern",
        "intern Trimble",
        "data intern Trimble"
    ]
    
    base_url = "https://www.indeed.com/rss"
    location = "United States"
    jobs_found = []
    
    for query in queries:
        print(f"📋 Testing: '{query}'")
        # Remove fromage to get all jobs
        rss_url = f"{base_url}?q={quote(query)}&l={quote(location)}&sort=date"
        
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                print(f"  ✅ Found {len(feed.entries)} job(s)")
                for entry in feed.entries[:10]:  # Get first 10
                    title = entry.get('title', '')
                    if 'intern' in title.lower():
                        jobs_found.append({
                            'title': title,
                            'company': 'Trimble',
                            'location': entry.get('where', 'United States'),
                            'url': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'summary': entry.get('summary', '')[:500]
                        })
                        print(f"    - {title}")
            else:
                print(f"  ⚠️  No jobs")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    if jobs_found:
        print(f"\n📊 Total Trimble intern jobs found: {len(jobs_found)}")
        print("\n📧 Sending test email...")
        send_test_email(jobs_found)
    else:
        print("\n⚠️  No Trimble intern jobs found at all")
        # Send a test email anyway to verify email works
        send_test_email([{
            'title': 'TEST: No Trimble jobs found - Email system works!',
            'company': 'Test',
            'location': 'Test Location',
            'url': 'https://www.indeed.com',
            'published': datetime.now().isoformat(),
            'summary': 'This is a test email to verify the email system is working. No Trimble intern jobs were found in the RSS feed.'
        }])

def send_test_email(jobs):
    """Send test email"""
    EMAIL_SENDER = "pavancseds@gmail.com"
    EMAIL_PASSWORD = "zkne yuqq uycz qckr"
    EMAIL_RECIPIENT = "pavancseds@gmail.com"
    
    try:
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .job {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; background-color: #f9f9f9; }}
                .job-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 5px; }}
                .company {{ color: #7f8c8d; font-size: 14px; margin-bottom: 5px; }}
                .location {{ color: #95a5a6; font-size: 12px; margin-bottom: 10px; }}
                .link {{ color: #3498db; text-decoration: none; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h2>🧪 Test Email - Trimble Internship Search Results</h2>
            <p>Found <strong>{len(jobs)}</strong> job(s):</p>
        """
        
        for job in jobs:
            html += f"""
            <div class="job">
                <div class="job-title">{job['title']}</div>
                <div class="company">🏢 {job['company']}</div>
                <div class="location">📍 {job['location']}</div>
                <div style="margin-top: 10px;">
                    <a href="{job['url']}" class="link" target="_blank">View Job →</a>
                </div>
                <div style="margin-top: 10px; font-size: 11px; color: #7f8c8d;">
                    {job['summary']}
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🧪 Test: {len(jobs)} Trimble Internship(s) Found"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECIPIENT
        
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print("✅ Email sent successfully!")
        print(f"📬 Check: {EMAIL_RECIPIENT}")
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_and_send_email()




