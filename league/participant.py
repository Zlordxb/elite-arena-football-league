"""
1. PARTICIPANT

Abstract base for anything that takes part in the league
(a human player or a team). Guarantees every participant
has a valid ID and a valid name.
"""

from abc import ABC, abstractmethod

from .validators import validate_id, validate_text


class Participant(ABC):
    def __init__(self, participant_id, name):
        self.id = validate_id(participant_id, "Participant ID")
        self.name = validate_text(name, "Name")

    @abstractmethod
    def get_info(self):
        """Return a plain dict describing this participant."""

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id!r}, name={self.name!r})"

    def __str__(self):
        return self.name
