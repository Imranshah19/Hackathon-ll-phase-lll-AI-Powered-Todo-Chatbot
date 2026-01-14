"""
Password hashing utilities using Argon2id.

Argon2id is the recommended algorithm by OWASP for password hashing:
- Memory-hard (resistant to GPU/ASIC attacks)
- Winner of the Password Hashing Competition (PHC)
- Provides both Argon2i and Argon2d properties
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Configure Argon2id with secure defaults
# These parameters balance security and performance
_hasher = PasswordHasher(
    time_cost=3,        # Number of iterations
    memory_cost=65536,  # 64 MB memory usage
    parallelism=4,      # Number of parallel threads
    hash_len=32,        # Length of the hash in bytes
    salt_len=16,        # Length of the random salt
)


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.

    Args:
        password: Plain text password to hash

    Returns:
        str: Argon2id hash string (includes algorithm params and salt)

    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> hashed.startswith("$argon2id$")
        True
    """
    return _hasher.hash(password)


def verify_password(hash: str, password: str) -> bool:
    """
    Verify a password against its Argon2id hash.

    Args:
        hash: The Argon2id hash string
        password: Plain text password to verify

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password(hashed, "my_password")
        True
        >>> verify_password(hashed, "wrong_password")
        False
    """
    try:
        _hasher.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False


__all__ = [
    "hash_password",
    "verify_password",
]
