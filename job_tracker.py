"""
Job tracking system to detect new job postings
"""
import json
import os
from datetime import datetime
from typing import Set, Dict, Any

class JobTracker:
    def __init__(self, db_file: str = "seen_jobs.json"):
        self.db_file = db_file
        self.seen_jobs: Set[str] = self._load_seen_jobs()
    
    def _load_seen_jobs(self) -> Set[str]:
        """Load seen job IDs from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('seen_job_ids', []))
            except (json.JSONDecodeError, IOError):
                return set()
        return set()
    
    def _save_seen_jobs(self):
        """Save seen job IDs to JSON file"""
        data = {
            'seen_job_ids': list(self.seen_jobs),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def is_new_job(self, job_id: str) -> bool:
        """Check if a job is new"""
        return job_id not in self.seen_jobs
    
    def mark_job_seen(self, job_id: str):
        """Mark a job as seen"""
        self.seen_jobs.add(job_id)
        self._save_seen_jobs()
    
    def get_new_jobs(self, jobs: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """Filter out already seen jobs and mark new ones as seen"""
        new_jobs = []
        for job in jobs:
            job_id = job.get('id', '')
            if job_id and self.is_new_job(job_id):
                new_jobs.append(job)
                self.mark_job_seen(job_id)
        return new_jobs

