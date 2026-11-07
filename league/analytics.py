"""
Season analytics derived from a Tournament: form guides, streaks,
head-to-head records, standings history, discipline and summaries.

Every function is read-only and works on plain Tournament objects,
so the UI (or a console script) can call them without extra state.
"""

from .constants import FORM_GUIDE_LENGTH, CardType, MatchResult


# ---------------------------------------------------------------------- #
# Form & streaks
# ---------------------------------------------------------------------- #
def team_form(tournament, team, limit=FORM_GUIDE_LENGTH):
    """
    A team's finished matches, oldest first, each as
    {"match", "matchday", "result", "opponent", "goals_for", "goals_against", "home"}.
    `limit` keeps only the most recent N results (None for all).
    """
    entries = []

    for match in tournament.finished_matches:
        if not match.involves(team):
            continue

        entries.append({
            "match": match,
            "matchday": match.matchday,
            "result": match.result_for(team),
            "opponent": match.opponent_of(team),
            "goals_for": match.goals_for(team),
            "goals_against": match.goals_against(team),
            "home": match.team1 is team,
        })

    return entries[-limit:] if limit else entries


def form_string(entries):
    """'WWDLW' (oldest -> newest)."""
    return "".join(entry["result"] for entry in entries)


def current_streak(entries):
    """('W', 3) for three wins in a row; None when there are no results."""
    if not entries:
        return None

    last = entries[-1]["result"]
    count = 0

    for entry in reversed(entries):
        if entry["result"] != last:
            break
        count += 1

    return (last, count)


def unbeaten_run(entries):
    """Number of consecutive most-recent matches without a loss."""
    count = 0

    for entry in reversed(entries):
        if entry["result"] == MatchResult.LOSS:
            break
        count += 1

    return count


# ---------------------------------------------------------------------- #
# Head-to-head
# ---------------------------------------------------------------------- #
def head_to_head(tournament, team_a, team_b):
    if team_a is team_b:
        raise ValueError("Pick two different teams to compare.")

    matches = [
        m for m in tournament.matches
        if m.involves(team_a) and m.involves(team_b)
    ]
    finished = [m for m in matches if m.is_finished]

    record = {
        "team_a": team_a,
        "team_b": team_b,
        "matches": matches,
        "played": len(finished),
        "wins_a": 0,
        "wins_b": 0,
        "draws": 0,
        "goals_a": 0,
        "goals_b": 0,
    }

    for match in finished:
        record["goals_a"] += match.goals_for(team_a)
        record["goals_b"] += match.goals_for(team_b)

        result = match.result_for(team_a)
        if result == MatchResult.WIN:
            record["wins_a"] += 1
        elif result == MatchResult.LOSS:
            record["wins_b"] += 1
        else:
            record["draws"] += 1

    return record


# ---------------------------------------------------------------------- #
# Standings over time
# ---------------------------------------------------------------------- #
def standings_by_matchday(tournament):
    """
    [{"matchday": 0, "standings": [...]}, {"matchday": 1, ...}, ...]
    Matchday 0 is the empty table; the last entry is the latest matchday
    that has at least one finished match.
    """
    if not tournament.matches:
        return []

    last = max((m.matchday for m in tournament.finished_matches), default=0)

    return [
        {
            "matchday": matchday,
            "standings": tournament.get_standings_after_matchday(matchday),
        }
        for matchday in range(0, last + 1)
    ]


def position_history_rows(tournament):
    """Flat rows for a position-race chart: matchday, team, rank, points."""
    rows = []

    for snapshot in standings_by_matchday(tournament):
        for row in snapshot["standings"]:
            rows.append({
                "matchday": snapshot["matchday"],
                "team": row["team"].name,
                "team_id": row["team"].id,
                "rank": row["rank"],
                "points": row["points"],
                "goal_difference": row["goal_difference"],
            })

    return rows


def goals_by_matchday(tournament):
    """Goals scored and matches finished per matchday (played matchdays only)."""
    rows = []

    for matchday, matches in tournament.matchdays.items():
        finished = [m for m in matches if m.is_finished]

        if not finished:
            continue

        rows.append({
            "matchday": matchday,
            "matches": len(finished),
            "goals": sum(m.total_goals for m in finished),
            "cards": sum(len(m.cards) for m in finished),
        })

    return rows


# ---------------------------------------------------------------------- #
# Season summary & discipline
# ---------------------------------------------------------------------- #
def results_breakdown(tournament):
    """How finished matches ended: home win / draw / away win."""
    breakdown = {"home_wins": 0, "draws": 0, "away_wins": 0}

    for match in tournament.finished_matches:
        if match.winner is match.team1:
            breakdown["home_wins"] += 1
        elif match.winner is match.team2:
            breakdown["away_wins"] += 1
        else:
            breakdown["draws"] += 1

    return breakdown


def clean_sheets(tournament):
    """{team_id: number of finished matches without conceding}."""
    sheets = {team.id: 0 for team in tournament.teams}

    for match in tournament.finished_matches:
        for team in match.teams:
            if match.goals_against(team) == 0:
                sheets[team.id] += 1

    return sheets


def season_summary(tournament):
    finished = tournament.finished_matches
    goals = sum(m.total_goals for m in finished)
    cards = [c for m in tournament.matches for c in m.cards]

    biggest_win = None
    highest_scoring = None

    for match in finished:
        margin = abs(match.score[0] - match.score[1])

        if margin > 0 and (
            biggest_win is None
            or margin > abs(biggest_win.score[0] - biggest_win.score[1])
        ):
            biggest_win = match

        if highest_scoring is None or match.total_goals > highest_scoring.total_goals:
            highest_scoring = match

    return {
        "phase": tournament.phase,
        "teams": len(tournament.teams),
        "active_teams": len(tournament.active_teams),
        "players": len(tournament.all_players),
        "fixtures": len(tournament.matches),
        "played": len(finished),
        "remaining": len(tournament.matches) - len(finished),
        "matchdays": tournament.total_matchdays,
        "current_matchday": tournament.current_matchday,
        "goals": goals,
        "goals_per_match": round(goals / len(finished), 2) if finished else 0.0,
        "yellow_cards": sum(1 for c in cards if c["card"] == CardType.YELLOW),
        "red_cards": sum(1 for c in cards if c["card"] == CardType.RED),
        "biggest_win": biggest_win,
        "highest_scoring": highest_scoring,
        **results_breakdown(tournament),
    }


def discipline_table(tournament):
    """One row per player who received at least one card, worst first."""
    rows = {}

    for match in tournament.matches:
        for card in match.cards:
            player = card["player"]
            row = rows.setdefault(player.id, {
                "player": player,
                "team": card["team"],
                "yellow": 0,
                "red": 0,
                "sent_off": 0,
            })

            if card["card"] == CardType.YELLOW:
                row["yellow"] += 1
            else:
                row["red"] += 1
                row["sent_off"] += 1

    return sorted(
        rows.values(),
        key=lambda r: (-r["red"], -r["yellow"], r["player"].name.casefold()),
    )


def team_stats(tournament, team):
    """Everything the UI shows on a team card, in one dict."""
    standing = next(
        row for row in tournament.get_standings() if row["team"] is team
    )
    form = team_form(tournament, team)
    all_form = team_form(tournament, team, limit=None)
    cards = [c for m in tournament.matches for c in m.cards_for_team(team)]

    return {
        **standing,
        "form": form,
        "form_string": form_string(form),
        "streak": current_streak(all_form),
        "unbeaten_run": unbeaten_run(all_form),
        "clean_sheets": clean_sheets(tournament)[team.id],
        "yellow_cards": sum(1 for c in cards if c["card"] == CardType.YELLOW),
        "red_cards": sum(1 for c in cards if c["card"] == CardType.RED),
        "players": len(team.players),
        "banned": len(team.banned_players),
    }
