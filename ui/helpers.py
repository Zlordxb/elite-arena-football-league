"""Converters from domain objects to display values / DataFrames."""

import pandas as pd

from league import MatchStatus


# ---------------------------------------------------------------------- #
# Text
# ---------------------------------------------------------------------- #
def score_text(match):
    if match.score is None:
        return "—"

    return f"{match.score[0]}  –  {match.score[1]}"


def result_text(match):
    """'Real Madrid won' / 'Draw' / '' for unfinished matches."""
    if not match.is_finished:
        return ""

    winner = match.winner
    return f"{winner.name} won" if winner else "Draw"


def player_label(player, with_team=True):
    label = f"{player.name} (#{player.id}), {player.role}"

    if with_team and player.team is not None:
        label = f"{label}, {player.team.name}"

    return label


def team_label(team):
    return f"{team.name} (ID {team.id})"


def match_label(match):
    return f"Matchday {match.matchday}: {match.team1.name} vs {match.team2.name}"


def fmt_stamp(moment):
    return moment.strftime("%d %b %H:%M") if moment else ""


def fmt_clock(moment):
    return moment.strftime("%H:%M:%S") if moment else ""


def minute_text(minute):
    return f"{minute}'" if minute is not None else "–"


def plural(count, singular, plural_form=None):
    """'1 draw' / '3 draws'."""
    word = singular if count == 1 else (plural_form or f"{singular}s")
    return f"{count} {word}"


def streak_text(streak):
    if not streak:
        return "–"
    result, count = streak
    singular, many = {"W": ("win", "wins"), "D": ("draw", "draws"), "L": ("loss", "losses")}[result]
    return plural(count, singular, many)


# ---------------------------------------------------------------------- #
# DataFrames
# ---------------------------------------------------------------------- #
def players_df(players):
    return pd.DataFrame([
        {
            "Player ID": str(p.id),
            "Name": p.name,
            "Role": p.role,
            "Status": "Banned" if p.is_banned else "Available",
        }
        for p in players
    ])


def teams_df(teams):
    return pd.DataFrame([
        {
            "ID": str(t.id),
            "Team": t.name,
            "Players": len(t.players),
            "Banned": len(t.banned_players),
            "Status": "Active" if t.is_active else "Inactive",
        }
        for t in teams
    ])


def cards_df(match):
    return pd.DataFrame([
        {
            "Minute": minute_text(card["minute"]),
            "Player": card["player"],
            "Team": card["team"],
            "Card": card["card"].title(),
            "Reason": card["reason"].replace("_", " ").title(),
        }
        for card in match.get_cards_report()
    ])


def timeline_df(events):
    return pd.DataFrame([
        {
            "Time": e.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Event": e.label,
            "Details": e.message,
            "Matchday": str(e.data.get("matchday") or ""),
            "Team": str(e.data.get("team") or ""),
        }
        for e in events
    ])


def discipline_df(rows):
    return pd.DataFrame([
        {
            "Player": r["player"].name,
            "Team": r["team"].name if r["team"] else "–",
            "Yellow": r["yellow"],
            "Red": r["red"],
        }
        for r in rows
    ])


# ---------------------------------------------------------------------- #
# Counters
# ---------------------------------------------------------------------- #
def match_counts(tournament):
    finished = len(tournament.get_matches_by_status(MatchStatus.FINISHED))
    live = len(tournament.get_matches_by_status(MatchStatus.LIVE))
    upcoming = len(tournament.get_matches_by_status(MatchStatus.UPCOMING))

    return {
        "total": len(tournament.matches),
        "finished": finished,
        "live": live,
        "upcoming": upcoming,
    }
