"""
Test suite for Authentication and Cryptographic hashing.
"""

import pytest
from Main import hash_password

def test_hash_password_consistency():
    hash1 = hash_password("mypassword123", "testuser")
    hash2 = hash_password("mypassword123", "testuser")
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 output length in hex

def test_hash_password_salt_uniqueness():
    # Different usernames produce different hashes even with same password
    hash_user1 = hash_password("samepass", "userA")
    hash_user2 = hash_password("samepass", "userB")
    assert hash_user1 != hash_user2

def test_hash_password_case_insensitivity_on_username():
    # Usernames are case-insensitive
    hash1 = hash_password("mypass", "DoctorWho")
    hash2 = hash_password("mypass", "doctorwho")
    assert hash1 == hash2

