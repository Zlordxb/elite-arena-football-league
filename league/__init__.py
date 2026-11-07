"""
League domain package (pure OOP, no UI dependencies).

    Participant (ABC)
    ├── HumanPlayer
    └── Team

    Match (ABC)
    └── FootballMatch

    Tournament  (teams, matchdays, standings, history)

Supporting modules:
    events      Event / EventLog (history)
    analytics   form, streaks, head-to-head, standings over time, summaries
    simulation  play fixtures with random results
    export      CSV rows, JSON snapshot, Markdown report
"""

from . import analytics, export, simulation
from .constants import (
    FORM_GUIDE_LENGTH,
    MAX_MATCH_MINUTE,
    PLAYER_ROLES,
    POINTS_FOR_DRAW,
    POINTS_FOR_LOSS,
    POINTS_FOR_WIN,
    CardType,
    MatchResult,
    MatchStatus,
    SeasonPhase,
    SendOffReason,
)
from .events import Event, EventLog, EventType
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
    "Event",
    "EventLog",
    "EventType",
    "MatchStatus",
    "MatchResult",
    "SeasonPhase",
    "CardType",
    "SendOffReason",
    "PLAYER_ROLES",
    "POINTS_FOR_WIN",
    "POINTS_FOR_DRAW",
    "POINTS_FOR_LOSS",
    "MAX_MATCH_MINUTE",
    "FORM_GUIDE_LENGTH",
    "build_sample_tournament",
    "analytics",
    "simulation",
    "export",
]
