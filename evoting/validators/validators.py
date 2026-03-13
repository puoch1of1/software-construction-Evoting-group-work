"""
Validation utilities for the E-Voting system.
Contains all input validation and transformation functions.
"""

import datetime
import hashlib
import random
import string

from ..config import (
    MIN_PASSWORD_LENGTH,
    VALID_GENDERS,
    POSITION_LEVELS,
    VOTER_CARD_LENGTH
)


def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> tuple:
    """
    Validate a date string.
    Returns (success, date_object or error_message).
    """
    try:
        date_obj = datetime.datetime.strptime(date_str, format_str)
        return True, date_obj
    except ValueError:
        return False, "Invalid date format."


def calculate_age(date_of_birth: datetime.datetime) -> int:
    """Calculate age from date of birth."""
    today = datetime.datetime.now()
    return (today - date_of_birth).days // 365


def validate_age_range(age: int, min_age: int, max_age: int = None) -> tuple:
    """
    Validate that age is within acceptable range.
    Returns (success, error_message or None).
    """
    if age < min_age:
        return False, f"Must be at least {min_age} years old. Current age: {age}"
    if max_age is not None and age > max_age:
        return False, f"Must not be older than {max_age}. Current age: {age}"
    return True, None


def validate_not_empty(value: str, field_name: str) -> tuple:
    """
    Validate that a string is not empty.
    Returns (success, error_message or None).
    """
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty."
    return True, None


def validate_password(password: str) -> tuple:
    """
    Validate password meets requirements.
    Returns (success, error_message or None).
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    return True, None


def validate_gender(gender: str) -> tuple:
    """
    Validate gender selection.
    Returns (success, normalized_value or error_message).
    """
    normalized = gender.upper()
    if normalized not in VALID_GENDERS:
        return False, "Invalid gender selection."
    return True, normalized


def validate_position_level(level: str) -> tuple:
    """
    Validate position level.
    Returns (success, normalized_value or error_message).
    """
    normalized = level.lower()
    if normalized not in POSITION_LEVELS:
        return False, "Invalid level."
    return True, normalized.capitalize()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_voter_card_number() -> str:
    """Generate a random voter card number."""
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=VOTER_CARD_LENGTH
        )
    )
