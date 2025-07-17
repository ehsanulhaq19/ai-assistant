import secrets
import string

def generate_session_id(length: int = 32) -> str:
    """
    Generate a random session ID using cryptographically secure random generation.
    
    Args:
        length: Length of the session ID (default: 32)
    
    Returns:
        A random string of specified length
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length)) 