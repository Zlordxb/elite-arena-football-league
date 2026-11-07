"""Dashboard: the season at a glance."""

import streamlit as st

from league import MatchStatus, SeasonPhase, analytics
from ui import charts
from ui.components import (
    empty_state,
    hero,
    results_list,
    scoreboard_strip,
    section,
    standings_table,
    stat_row,
    timeline,
)
from ui.helpers import plural
from ui.state import nav_button

RECENT_RESULTS = 6
TIMELINE_ITEMS = 8


def render(tournament):
    summary = analytics.season_summary(tournament)
    standings = tournament.get_standings()
    leader = standings[0] if standings else None

    hero(tournament, summary, leader)

    if not tournament.teams:
        _setup_guide()
        return

    _matchday_strip(tournament)

    if summary["fixtures"]:
        _kpis(summary)

    if not summary["played"]:
        _table_only(tournament, standings)
        return

    left, right = st.columns([1.45, 1], gap="large")
    with left:
        section("League table", "Points, then goal difference, then goals scored")
        standings_table(tournament, standings, compact=len(standings) > 5)
    with right:
        section("Points", "Ranked by current position")
        with st.container(border=True, key="card-dash-points"):
            st.altair_chart(charts.points_bar(standings), width="stretch", theme=None)

    left, right = st.columns([1.45, 1], gap="large")
    with left:
        _position_race(tournament, standings)
    with right:
        section("Goal difference", "Scored minus conceded")
        with st.container(border=True, key="card-dash-gd"):
            st.altair_chart(charts.goal_difference_bar(standings), width="stretch", theme=None)

    left, right = st.columns([1, 1.45], gap="large")
    with left:
        section("Latest results", f"Last {RECENT_RESULTS}")
        with st.container(border=True, key="card-dash-results"):
            results_list(list(reversed(tournament.finished_matches))[:RECENT_RESULTS])
    with right:
        section("Activity", "Most recent first")
        with st.container(border=True, key="card-dash-timeline"):
            timeline(tournament.get_timeline(), limit=TIMELINE_ITEMS)
        nav_button("Open full history", "History", key="dash_to_history")


# ---------------------------------------------------------------------- #
# Sections
# ---------------------------------------------------------------------- #
def _setup_guide():
    empty_state(
        "Set up your league",
        "Three steps and the season is ready to play.",
        steps=(
            "Register at least two teams in Manage League.",
            "Add players to each squad in Teams & Players.",
            "Generate the schedule, then start matches from Fixtures.",
        ),
        icon_name="trophy",
    )
    nav_button("Go to Manage League", "Manage League", key="dash_to_manage", kind="primary")


def _matchday_strip(tournament):
    live = tournament.get_matches_by_status(MatchStatus.LIVE)
    phase = tournament.phase

    if phase == SeasonPhase.SETUP:
        empty_state(
            "One more team needed",
            "A schedule needs at least two active teams. Register another team in Manage League.",
        )
        nav_button("Go to Manage League", "Manage League", key="dash_to_manage2", kind="primary")
        return

    if phase == SeasonPhase.READY:
        empty_state(
            "Ready for kick-off",
            "Teams are registered. Generate the round-robin schedule to create the fixtures.",
        )
        nav_button("Generate schedule in Manage League", "Manage League", key="dash_to_manage3", kind="primary")
        return

    if live:
        section("Live now", f"{len(live)} in progress")
        scoreboard_strip(live)
        nav_button("Update live matches", "Fixtures", key="dash_to_fixtures_live")
        return

    matchday = tournament.current_matchday or tournament.total_matchdays
    matches = tournament.matchdays.get(matchday, [])
    played = sum(1 for m in matches if m.is_finished)

    if tournament.is_complete:
        section(f"Final matchday {matchday}", "Season complete")
    else:
        section(f"Matchday {matchday}", f"{played} of {len(matches)} played")

    scoreboard_strip(matches)

    if not tournament.is_complete:
        nav_button("Open fixtures", "Fixtures", key="dash_to_fixtures")


def _kpis(summary):
    cards = f"{summary['yellow_cards']} yellow, {summary['red_cards']} red"
    stat_row([
        {"label": "Fixtures played", "value": summary["played"], "unit": f"of {summary['fixtures']}",
         "note": f"{summary['remaining']} remaining", "icon_name": "calendar-check"},
        {"label": "Goals", "value": summary["goals"], "note": f"{summary['goals_per_match']} per match",
         "icon_name": "goal"},
        {"label": "Results", "value": summary["home_wins"] + summary["away_wins"],
         "unit": "decided", "note": plural(summary["draws"], "draw"), "icon_name": "medal"},
        {"label": "Cards", "value": summary["yellow_cards"] + summary["red_cards"], "note": cards,
         "icon_name": "rectangle-vertical"},
    ])


def _table_only(tournament, standings):
    section("League table", "No results yet")
    standings_table(tournament, standings)


def _position_race(tournament, standings):
    rows = analytics.position_history_rows(tournament)
    names = [row["team"].name for row in standings]

    head, pick = st.columns([1.3, 1], vertical_alignment="bottom")
    with head:
        section("Position race", "After every matchday")
    with pick:
        highlight = st.selectbox(
            "Highlight team", names, key="dash_highlight", label_visibility="collapsed"
        )

    with st.container(border=True, key="card-dash-race"):
        if len(rows) <= len(names):
            st.caption("The race starts after the first matchday is played.")
        else:
            st.altair_chart(charts.position_race(rows, highlight), width="stretch", theme=None)
