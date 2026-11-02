"""
League domain package (pure OOP, no UI dependencies).

    Participant (ABC)
    ├── HumanPlayer
    └── Team

    Match (ABC)
    └── FootballMatch

    Tournament
"""

from .constants import (
    PLAYER_ROLES,
    POINTS_FOR_DRAW,
    POINTS_FOR_LOSS,
    POINTS_FOR_WIN,
    CardType,
    MatchStatus,
    SendOffReason,
)
from .football_match import FootballMatch
from .match import Match
from .participant import Participant
from .player import HumanPlayer
from .sample_data import build_sample_tournament
from .team import Team
from .tournament import Tournament

__all__ = [
    "Participant",
    "HumanPlayer",
    "Team",
    "Match",
    "FootballMatch",
    "Tournament",
    "MatchStatus",
    "CardType",
    "SendOffReason",
    "PLAYER_ROLES",
    "POINTS_FOR_WIN",
    "POINTS_FOR_DRAW",
    "POINTS_FOR_LOSS",
    "build_sample_tournament",
]
