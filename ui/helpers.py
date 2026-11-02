"""Converters from domain objects to display values / DataFrames."""

import pandas as pd

from league import MatchStatus


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
    label = f"{player.name} (#{player.id}) · {player.role}"

    if with_team and player.team is not None:
        label = f"{label} · {player.team.name}"

    return label


def team_label(team):
    return f"{team.name}  ·  ID {team.id}"


# ---------------------------------------------------------------------- #
# DataFrames
# ---------------------------------------------------------------------- #
def standings_df(tournament):
    """Table rows come straight from Tournament.get_standings()."""
    rows = [
        {
            "Pos": row["rank"],
            "Team": row["team"].name,
            "P": row["played"],
            "W": row["won"],
            "D": row["drawn"],
            "L": row["lost"],
            "GF": row["goals_for"],
            "GA": row["goals_against"],
            "GD": row["goal_difference"],
            "PTS": row["points"],
        }
        for row in tournament.get_standings()
    ]
    return pd.DataFrame(rows)


def players_df(players):
    return pd.DataFrame([
        {
            "Player ID": p.id,
            "Name": p.name,
            "Role": p.role,
            "Status": "Banned" if p.is_banned else "Available",
        }
        for p in players
    ])


def teams_df(teams):
    return pd.DataFrame([
        {
            "ID": t.id,
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
            "Player": card["player"],
            "Team": card["team"],
            "Card": card["card"].title(),
            "Reason": card["reason"].replace("_", " ").title(),
        }
        for card in match.get_cards_report()
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
