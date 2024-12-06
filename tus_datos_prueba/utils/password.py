import bcrypt

def create_password(text: str) -> bytes:
    password_bytes = text.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_password

def verify_password(password: str, hashed_password: bytes) -> bool:
    password_bytes = password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_password)
