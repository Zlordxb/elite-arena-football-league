"""
Reusable validation helpers.

Every class in the domain used to repeat the same "is it empty?" checks.
Centralising them keeps the error messages consistent and the classes short.
"""


def validate_id(value, label="ID"):
    """
    Accept a non-empty string or a (non-bool) integer and return it normalised.

    Strings are stripped so " 1 " and "1" are treated as the same ID.
    """
    if isinstance(value, bool):
        raise ValueError(f"{label} cannot be a boolean.")

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()
        if value:
            return value
        raise ValueError(f"{label} cannot be empty.")

    raise ValueError(f"{label} must be a non-empty string or an integer.")


def validate_text(value, label="Value", min_length=1):
    """Accept a non-empty string and return it stripped."""
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string.")

    value = value.strip()

    if len(value) < min_length:
        if min_length == 1:
            raise ValueError(f"{label} cannot be empty.")
        raise ValueError(
            f"{label} must contain at least {min_length} characters."
        )

    return value


def validate_choice(value, choices, label="Value"):
    """
    Accept a string that matches one of `choices` (case-insensitive)
    and return the canonical spelling from `choices`.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be empty.")

    normalised = value.strip().casefold()

    for choice in choices:
        if choice.casefold() == normalised:
            return choice

    allowed = ", ".join(repr(c) for c in choices)
    raise ValueError(f"Invalid {label.lower()}. Use one of: {allowed}.")


def validate_score(value, label="Score"):
    """Accept a non-negative integer (bool is rejected on purpose)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a non-negative integer.")

    if value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")

    return value
