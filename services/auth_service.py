from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    """Hash a password for storing."""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """Verify a stored password against a user input password."""
    return check_password_hash(hashed_password, password)
