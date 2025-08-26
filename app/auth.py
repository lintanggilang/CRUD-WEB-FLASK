import hashlib
from .models import User, Permission

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(db, username: str, password: str):
    password_hash = hash_password(password)
    return db.query(User).filter(User.username == username, User.password_hash == password_hash).first()

def get_user_permissions(db, user_id: int):
    return db.query(Permission).filter(Permission.user_id == user_id).all()