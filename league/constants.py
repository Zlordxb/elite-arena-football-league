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

MIN_TOURNAMENT_NAME_LENGTH = 3
MIN_TEAMS_FOR_SCHEDULE = 2
