from flask_sqlalchemy import SQLAlchemy
from app.tenant import get_tenant

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    tenant = db.Column(db.String(50), default=get_tenant)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='pending')