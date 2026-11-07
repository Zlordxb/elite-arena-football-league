"""
4. MATCH

Abstract base for a fixture between two teams.
Enforces the lifecycle Upcoming -> Live -> Finished and score validation,
and keeps its own event log (kick-off, full time, ...).
"""

from abc import ABC, abstractmethod
from datetime import datetime

from .constants import MatchResult, MatchStatus
from .events import EventLog, EventType
from .team import Team
from .validators import validate_id, validate_score


class Match(ABC):
    VALID_STATUSES = MatchStatus.ALL

    def __init__(self, match_id, team1, team2):
        if not isinstance(team1, Team) or not isinstance(team2, Team):
            raise TypeError("A match requires two Team objects.")

        if team1 is team2 or team1.id == team2.id:
            raise ValueError("A team cannot play against itself.")

        self.match_id = validate_id(match_id, "Match ID")
        self.team1 = team1
        self.team2 = team2

        self.score = None
        self.status = MatchStatus.UPCOMING

        # History
        self.matchday = None        # set by Tournament.generate_schedule
        self.started_at = None
        self.finished_at = None
        self.events = EventLog()

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def start_match(self):
        if not self.is_upcoming:
            raise RuntimeError("Only upcoming matches can be started.")

        if not self.team1.is_active or not self.team2.is_active:
            raise RuntimeError("Both teams must be active.")

        self.status = MatchStatus.LIVE
        self.started_at = datetime.now()
        self.events.record(
            EventType.MATCH_STARTED,
            f"Kick-off: {self.team1.name} vs {self.team2.name}.",
            match_id=self.match_id,
            matchday=self.matchday,
        )

    def finish_match(self, team1_score, team2_score):
        if not self.is_live:
            raise RuntimeError("Only live matches can be finished.")

        team1_score = validate_score(team1_score, f"{self.team1.name} score")
        team2_score = validate_score(team2_score, f"{self.team2.name} score")

        self.score = (team1_score, team2_score)
        self.status = MatchStatus.FINISHED
        self.finished_at = datetime.now()
        self.events.record(
            EventType.MATCH_FINISHED,
            f"Full time: {self.team1.name} {team1_score} - {team2_score} "
            f"{self.team2.name}.",
            match_id=self.match_id,
            matchday=self.matchday,
            score=f"{team1_score}-{team2_score}",
        )

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    @property
    def is_upcoming(self):
        return self.status == MatchStatus.UPCOMING

    @property
    def is_live(self):
        return self.status == MatchStatus.LIVE

    @property
    def is_finished(self):
        return self.status == MatchStatus.FINISHED

    @property
    def teams(self):
        return (self.team1, self.team2)

    def involves(self, team):
        return team is self.team1 or team is self.team2

    def opponent_of(self, team):
        if team is self.team1:
            return self.team2
        if team is self.team2:
            return self.team1
        raise ValueError("Team is not playing in this match.")

    def goals_for(self, team):
        if not self.is_finished:
            return None
        return self.score[0] if team is self.team1 else self.score[1]

    def goals_against(self, team):
        if not self.is_finished:
            return None
        return self.score[1] if team is self.team1 else self.score[0]

    def result_for(self, team):
        """'W', 'D' or 'L' for `team`; None while the match is unfinished."""
        if not self.is_finished:
            return None

        if not self.involves(team):
            raise ValueError("Team is not playing in this match.")

        goals_for = self.goals_for(team)
        goals_against = self.goals_against(team)

        if goals_for > goals_against:
            return MatchResult.WIN
        if goals_for < goals_against:
            return MatchResult.LOSS
        return MatchResult.DRAW

    @property
    def winner(self):
        """Winning Team, or None for a draw / unfinished match."""
        if not self.is_finished:
            return None

        score1, score2 = self.score

        if score1 > score2:
            return self.team1
        if score2 > score1:
            return self.team2
        return None

    @property
    def total_goals(self):
        return sum(self.score) if self.is_finished else 0

    def get_result(self):
        if not self.is_finished:
            return None

        winner = self.winner

        return {
            "match_id": self.match_id,
            "team1": self.team1.name,
            "team2": self.team2.name,
            "score": self.score,
            "winner": winner.name if winner else "Draw",
            "status": self.status,
        }

    @abstractmethod
    def get_match_details(self):
        """Return a plain dict with sport-specific details."""

    def __repr__(self):
        return (
            f"{type(self).__name__}(id={self.match_id!r}, "
            f"{self.team1.name!r} vs {self.team2.name!r}, {self.status})"
        )
