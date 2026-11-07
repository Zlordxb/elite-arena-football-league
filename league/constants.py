"""
Shared constants for the league domain.

Keeping every "magic value" here means the rules of the league
(points, statuses, card types, roles) live in one place.
"""


class MatchStatus:
    """Lifecycle of a match: Upcoming -> Live -> Finished."""

    UPCOMING = "Upcoming"
    LIVE = "Live"
    FINISHED = "Finished"

    ALL = (UPCOMING, LIVE, FINISHED)


class MatchResult:
    """Outcome of a finished match from one team's point of view."""

    WIN = "W"
    DRAW = "D"
    LOSS = "L"

    ALL = (WIN, DRAW, LOSS)


class SeasonPhase:
    """Where the tournament is in its life."""

    SETUP = "Setup"               # fewer than two active teams registered
    READY = "Ready"               # enough teams, schedule not generated yet
    IN_PROGRESS = "In progress"   # schedule exists, matches still to play
    COMPLETE = "Complete"         # every fixture finished

    ALL = (SETUP, READY, IN_PROGRESS, COMPLETE)


class CardType:
    """Disciplinary cards that can be shown during a football match."""

    YELLOW = "yellow"
    RED = "red"

    ALL = (YELLOW, RED)


class SendOffReason:
    """Why a player was sent off (recorded with every red card)."""

    SECOND_YELLOW = "second_yellow"
    DIRECT_RED = "direct_red"


# Allowed positions for a HumanPlayer (matched case-insensitively).
PLAYER_ROLES = ("Goalkeeper", "Defender", "Midfielder", "Forward")

# League rules.
POINTS_FOR_WIN = 3
POINTS_FOR_DRAW = 1
POINTS_FOR_LOSS = 0

YELLOW_CARDS_FOR_SEND_OFF = 2

# A card can be recorded from the 1st minute up to the end of extra time.
MAX_MATCH_MINUTE = 120

# How many recent results make up a team's form guide.
FORM_GUIDE_LENGTH = 5

MIN_TOURNAMENT_NAME_LENGTH = 3
MIN_TEAMS_FOR_SCHEDULE = 2
