"""
Result simulation: plays fixtures with random (but plausible) scores
and the occasional card. Useful for demos and for filling a season
quickly so the history / analytics views have something to show.

Every simulated action goes through the normal Tournament facade,
so all league rules still apply and every event is recorded.
"""

import random

from .constants import MAX_MATCH_MINUTE, CardType

# Goals per team per match, weighted towards realistic football scores.
GOAL_WEIGHTS = {0: 22, 1: 32, 2: 24, 3: 13, 4: 6, 5: 3}

# How many cards a simulated match produces, and how often one is red.
CARD_COUNT_WEIGHTS = {0: 30, 1: 30, 2: 22, 3: 12, 4: 6}
RED_CARD_PROBABILITY = 0.12
REGULAR_TIME_MINUTES = 90


def _rng(rng):
    return rng if rng is not None else random


def random_goals(rng=None):
    rng = _rng(rng)
    goals, weights = zip(*GOAL_WEIGHTS.items())
    return rng.choices(goals, weights=weights)[0]


def simulate_match(tournament, match, rng=None, with_cards=True):
    """Start `match`, optionally show some cards, then finish it."""
    rng = _rng(rng)

    if not match.is_upcoming:
        raise RuntimeError("Only upcoming matches can be simulated.")

    tournament.start_match(match.match_id)

    if with_cards:
        _simulate_cards(tournament, match, rng)

    tournament.finish_match(
        match.match_id, random_goals(rng), random_goals(rng)
    )
    return match


def _simulate_cards(tournament, match, rng):
    counts, weights = zip(*CARD_COUNT_WEIGHTS.items())
    how_many = rng.choices(counts, weights=weights)[0]
    minutes = sorted(rng.randint(1, REGULAR_TIME_MINUTES) for _ in range(how_many))

    for minute in minutes:
        candidates = [
            p for p in match.team1.available_players + match.team2.available_players
            if not match.is_sent_off(p)
        ]

        if not candidates:
            break

        player = rng.choice(candidates)
        card = CardType.RED if rng.random() < RED_CARD_PROBABILITY else CardType.YELLOW
        tournament.record_card(
            match.match_id, player.id, card, min(minute, MAX_MATCH_MINUTE)
        )


def _playable(match):
    return match.is_upcoming and match.team1.is_active and match.team2.is_active


def simulate_matchday(tournament, matchday, rng=None, with_cards=True):
    """Play every upcoming match of one matchday. Returns the matches played."""
    rng = _rng(rng)
    matches = tournament.matchdays.get(matchday)

    if matches is None:
        raise ValueError(f"Matchday {matchday} does not exist.")

    return [
        simulate_match(tournament, m, rng, with_cards)
        for m in matches
        if _playable(m)
    ]


def simulate_next_matchday(tournament, rng=None, with_cards=True):
    """Play the first matchday that still has upcoming matches."""
    matchday = tournament.current_matchday

    if matchday is None:
        raise RuntimeError("There are no matchdays left to play.")

    return simulate_matchday(tournament, matchday, rng, with_cards)


def simulate_season(tournament, rng=None, with_cards=True):
    """Play every remaining upcoming match, matchday by matchday."""
    rng = _rng(rng)
    played = []

    for matchday in tournament.matchdays:
        played.extend(simulate_matchday(tournament, matchday, rng, with_cards))

    if not played:
        raise RuntimeError("There are no upcoming matches to simulate.")

    return played
