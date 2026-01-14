"""
Unit tests for password hashing utilities.

Tests:
- T014: Password hash and verify functions using Argon2id
"""

import pytest


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_password_returns_string(self, valid_password: str) -> None:
        """hash_password should return a string hash."""
        from src.auth.password import hash_password

        hashed = hash_password(valid_password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_not_plaintext(self, valid_password: str) -> None:
        """hash_password should NOT return the plaintext password."""
        from src.auth.password import hash_password

        hashed = hash_password(valid_password)

        assert hashed != valid_password

    def test_hash_password_uses_argon2(self, valid_password: str) -> None:
        """hash_password should use Argon2id algorithm."""
        from src.auth.password import hash_password

        hashed = hash_password(valid_password)

        # Argon2 hashes start with $argon2
        assert hashed.startswith("$argon2")

    def test_hash_password_unique_per_call(self, valid_password: str) -> None:
        """hash_password should produce different hashes each time (salted)."""
        from src.auth.password import hash_password

        hash1 = hash_password(valid_password)
        hash2 = hash_password(valid_password)

        # Same password should produce different hashes due to random salt
        assert hash1 != hash2

    def test_verify_password_correct(self, valid_password: str) -> None:
        """verify_password should return True for correct password."""
        from src.auth.password import hash_password, verify_password

        hashed = hash_password(valid_password)
        result = verify_password(hashed, valid_password)

        assert result is True

    def test_verify_password_incorrect(self, valid_password: str) -> None:
        """verify_password should return False for incorrect password."""
        from src.auth.password import hash_password, verify_password

        hashed = hash_password(valid_password)
        result = verify_password(hashed, "wrong_password")

        assert result is False

    def test_verify_password_empty_fails(self, valid_password: str) -> None:
        """verify_password should return False for empty password."""
        from src.auth.password import hash_password, verify_password

        hashed = hash_password(valid_password)
        result = verify_password(hashed, "")

        assert result is False

    def test_hash_empty_password(self) -> None:
        """hash_password should handle empty password (implementation may vary)."""
        from src.auth.password import hash_password

        # Empty password should still produce a hash
        # (validation should happen at schema level)
        hashed = hash_password("")

        assert isinstance(hashed, str)
        assert hashed.startswith("$argon2")
