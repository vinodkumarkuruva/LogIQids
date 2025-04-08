from Log import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    referral_code = db.Column(db.String(10), unique=True, nullable=False, default=lambda: str(uuid.uuid4())[:10])
    password_hash = db.Column(db.String(128), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    referrer = db.relationship('User', remote_side=[id], backref=db.backref('referees', lazy='dynamic'))


    
