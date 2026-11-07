"""
Exports: flat rows for tables / CSV, a JSON snapshot of the whole
tournament, and a Markdown season report.

No pandas here on purpose: the domain package stays dependency-free.
"""

import csv
import io
import json

from . import analytics


# ---------------------------------------------------------------------- #
# Flat rows
# ---------------------------------------------------------------------- #
def standings_rows(tournament):
    return [
        {
            "rank": row["rank"],
            "team": row["team"].name,
            "played": row["played"],
            "won": row["won"],
            "drawn": row["drawn"],
            "lost": row["lost"],
            "goals_for": row["goals_for"],
            "goals_against": row["goals_against"],
            "goal_difference": row["goal_difference"],
            "points": row["points"],
            "form": analytics.form_string(analytics.team_form(tournament, row["team"])),
        }
        for row in tournament.get_standings()
    ]


def fixtures_rows(tournament):
    return [
        {
            "match_id": m.match_id,
            "matchday": m.matchday,
            "home": m.team1.name,
            "away": m.team2.name,
            "home_goals": m.score[0] if m.score else None,
            "away_goals": m.score[1] if m.score else None,
            "status": m.status,
            "winner": (m.winner.name if m.winner else ("Draw" if m.is_finished else None)),
            "started_at": _stamp(m.started_at),
            "finished_at": _stamp(m.finished_at),
            "yellow_cards": len(m.yellow_cards),
            "red_cards": len(m.red_cards),
        }
        for m in tournament.matches
    ]


def players_rows(tournament):
    return [
        {
            "player_id": p.id,
            "name": p.name,
            "role": p.role,
            "team": p.team.name if p.team else None,
            "banned": p.is_banned,
        }
        for p in tournament.all_players
    ]


def cards_rows(tournament):
    rows = []

    for match in tournament.matches:
        for card in match.get_cards_report():
            rows.append({
                "match_id": match.match_id,
                "matchday": match.matchday,
                "fixture": f"{match.team1.name} vs {match.team2.name}",
                **card,
            })

    return rows


def timeline_rows(tournament):
    return [event.to_dict() for event in tournament.get_timeline(newest_first=False)]


def rows_to_csv(rows, fieldnames=None):
    """Serialise a list of flat dicts to CSV text (header included)."""
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


# ---------------------------------------------------------------------- #
# JSON snapshot
# ---------------------------------------------------------------------- #
def tournament_to_dict(tournament):
    return {
        "name": tournament.name,
        "created_at": _stamp(tournament.created_at),
        "phase": tournament.phase,
        "schedule_generated": tournament.schedule_generated,
        "teams": [
            {
                **team.get_info(),
                "players": [p.get_info() for p in team.players],
            }
            for team in tournament.teams
        ],
        "matches": [
            {
                **match.get_match_details(),
                "started_at": _stamp(match.started_at),
                "finished_at": _stamp(match.finished_at),
                "cards": match.get_cards_report(),
                "events": [e.to_dict() for e in match.events],
            }
            for match in tournament.matches
        ],
        "standings": standings_rows(tournament),
        "summary": _summary_for_json(analytics.season_summary(tournament)),
        "history": [e.to_dict() for e in tournament.history],
    }


def to_json(tournament, indent=2):
    return json.dumps(tournament_to_dict(tournament), indent=indent, default=str)


# ---------------------------------------------------------------------- #
# Markdown report
# ---------------------------------------------------------------------- #
def season_report_markdown(tournament):
    summary = analytics.season_summary(tournament)
    lines = [
        f"# {tournament.name} - Season report",
        "",
        f"Phase: **{summary['phase']}**  ",
        f"Teams: {summary['teams']} | Fixtures: {summary['fixtures']} | "
        f"Played: {summary['played']} | Goals: {summary['goals']} "
        f"({summary['goals_per_match']} per match) | "
        f"Cards: {summary['yellow_cards']} yellow, {summary['red_cards']} red",
        "",
        "## Standings",
        "",
        "| # | Team | P | W | D | L | GF | GA | GD | Pts | Form |",
        "|---|------|---|---|---|---|----|----|----|-----|------|",
    ]

    for row in standings_rows(tournament):
        lines.append(
            f"| {row['rank']} | {row['team']} | {row['played']} | {row['won']} | "
            f"{row['drawn']} | {row['lost']} | {row['goals_for']} | "
            f"{row['goals_against']} | {row['goal_difference']} | {row['points']} | "
            f"{row['form'] or '-'} |"
        )

    lines += ["", "## Results by matchday", ""]

    if not tournament.matches:
        lines.append("_No schedule generated yet._")

    for matchday, matches in tournament.matchdays.items():
        lines.append(f"### Matchday {matchday}")
        lines.append("")

        for m in matches:
            score = f"{m.score[0]} - {m.score[1]}" if m.score else "vs"
            lines.append(f"- {m.team1.name} {score} {m.team2.name} ({m.status})")

        lines.append("")

    discipline = analytics.discipline_table(tournament)

    if discipline:
        lines += [
            "## Discipline",
            "",
            "| Player | Team | Yellow | Red |",
            "|--------|------|--------|-----|",
        ]
        for row in discipline:
            lines.append(
                f"| {row['player'].name} | {row['team'].name if row['team'] else '-'} | "
                f"{row['yellow']} | {row['red']} |"
            )
        lines.append("")

    if summary["biggest_win"] is not None:
        m = summary["biggest_win"]
        lines.append(
            f"Biggest win: {m.team1.name} {m.score[0]} - {m.score[1]} {m.team2.name}  "
        )

    if summary["highest_scoring"] is not None:
        m = summary["highest_scoring"]
        lines.append(
            f"Highest-scoring match: {m.team1.name} {m.score[0]} - {m.score[1]} "
            f"{m.team2.name}"
        )

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #
def _stamp(value):
    return value.isoformat(timespec="seconds") if value else None


def _summary_for_json(summary):
    def describe(match):
        if match is None:
            return None
        return f"{match.team1.name} {match.score[0]} - {match.score[1]} {match.team2.name}"

    return {
        **summary,
        "biggest_win": describe(summary["biggest_win"]),
        "highest_scoring": describe(summary["highest_scoring"]),
    }
