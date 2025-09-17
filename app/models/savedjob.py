from app import db
from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash,check_password_hash

class SavedJob(db.Model):
 __tablename__ = "saved_jobs"
 id = db.Column(db.Integer, primary_key=True)
 created_at = db.Column(db.DateTime, default=datetime.utcnow)
 student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
 job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))