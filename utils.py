"""
Shared utility helpers for the E-Voting system.
Provides reusable functions used across multiple service modules.
"""


def apply_updates(entity: dict, updates: dict) -> dict:
    """
    Apply a partial updates dict to an entity dict in-place.

    Only keys whose values are not None and not an empty string are applied,
    so callers can pass an updates dict that contains blank fields from user
    input without accidentally erasing existing data.

    Args:
        entity:  The original entity dict to update (mutated in-place).
        updates: A dict of fields to apply.

    Returns:
        The updated entity dict (same object that was passed in).
    """
    for key, value in updates.items():
        if value is not None and value != "":
            entity[key] = value
    return entity
