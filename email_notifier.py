"""
Email notification system for new job postings
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT, SMTP_SERVER, SMTP_PORT

class EmailNotifier:
    def __init__(self):
        self.sender = EMAIL_SENDER
        self.password = EMAIL_PASSWORD
        self.recipient = EMAIL_RECIPIENT
    
    def _create_email_body(self, jobs: List[Dict[str, Any]]) -> str:
        """Create HTML email body with job listings"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .job { 
                    border: 1px solid #ddd; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
                .job-title { 
                    font-size: 18px; 
                    font-weight: bold; 
                    color: #2c3e50;
                    margin-bottom: 5px;
                }
                .posted-time {
                    color: #27ae60;
                    font-size: 12px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .company { 
                    color: #7f8c8d; 
                    font-size: 14px;
                    margin-bottom: 5px;
                }
                .location { 
                    color: #95a5a6; 
                    font-size: 12px;
                    margin-bottom: 10px;
                }
                .link { 
                    color: #3498db; 
                    text-decoration: none;
                    font-weight: bold;
                }
                .link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h2>🎯 New Job Postings Found!</h2>
            <p>Found <strong>{count}</strong> new job(s) matching your criteria:</p>
        """.format(count=len(jobs))
        
        for job in jobs:
            posted_info = ""
            if job.get('published_date'):
                try:
                    from datetime import datetime
                    posted_date = datetime.fromisoformat(job['published_date'])
                    age = datetime.now() - posted_date
                    age_hours = age.total_seconds() / 3600
                    if age_hours < 1:
                        posted_info = f'<div class="posted-time">⚡ Just posted ({int(age_hours*60)} minutes ago)</div>'
                    else:
                        posted_info = f'<div class="posted-time">⚡ Posted {age_hours:.1f} hours ago</div>'
                except:
                    pass
            
            html += f"""
            <div class="job">
                <div class="job-title">{job.get('title', 'N/A')}</div>
                {posted_info}
                <div class="company">🏢 {job.get('company', 'N/A')}</div>
                <div class="location">📍 {job.get('location', 'N/A')}</div>
                <div style="margin-top: 10px;">
                    <a href="{job.get('url', '#')}" class="link" target="_blank">View Job →</a>
                </div>
            </div>
            """
        
        html += """
            <p style="margin-top: 20px; color: #7f8c8d; font-size: 12px;">
                Good luck with your applications! 🚀
            </p>
        </body>
        </html>
        """
        return html
    
    def send_notification(self, jobs: List[Dict[str, Any]]):
        """Send email notification with new job listings"""
        if not self.sender or not self.password or not self.recipient:
            print("⚠️  Email configuration missing. Please set EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECIPIENT in .env")
            return
        
        if not jobs:
            return
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 {len(jobs)} New Job Posting(s) Found!"
            msg['From'] = self.sender
            msg['To'] = self.recipient
            
            html_body = self._create_email_body(jobs)
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully for {len(jobs)} new job(s)")
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")

