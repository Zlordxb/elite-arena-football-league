"""History: the timeline, results by matchday, the table over time and trends."""

import streamlit as st

from league import EventType, analytics, export
from ui import charts
from ui.components import (
    empty_state,
    page_header,
    results_list,
    section,
    standings_table,
    stat_row,
    tab_bar,
    timeline,
)
from ui.helpers import discipline_df, timeline_df
from ui.state import nav_button

EVENT_GROUPS = {
    "All": None,
    "Matches": (EventType.MATCH_STARTED, EventType.MATCH_FINISHED),
    "Cards": (EventType.CARD, EventType.SEND_OFF),
    "Teams": EventType.TEAM_EVENTS,
    "Players": EventType.PLAYER_EVENTS,
}
PAGE_SIZE = 40


def render(tournament):
    page_header("History", "Everything that happened this season, in order.", icon_name="history")

    events = tournament.get_timeline()

    if not events:
        empty_state("Nothing recorded yet", "Register a team or play a match and it shows up here.",
                    icon_name="history")
        nav_button("Go to Manage League", "Manage League", key="hi_to_manage", kind="primary")
        return

    sections = {
        "Timeline": lambda: _timeline_tab(tournament, events),
        "Results by matchday": lambda: _results_tab(tournament),
        "Table over time": lambda: _table_tab(tournament),
        "Trends": lambda: _trends_tab(tournament),
    }
    selected = tab_bar("history_tabs", list(sections))
    sections[selected]()


# ---------------------------------------------------------------------- #
# Timeline
# ---------------------------------------------------------------------- #
def _timeline_tab(tournament, events):
    f1, f2, f3 = st.columns([2, 1.4, 1], vertical_alignment="bottom")
    with f1:
        group = st.segmented_control(
            "Show", list(EVENT_GROUPS), default="All", key="hi_group"
        ) or "All"
    with f2:
        team_names = ["All teams"] + [t.name for t in tournament.teams]
        team_name = st.selectbox("Team", team_names, key="hi_team")
    with f3:
        as_table = st.toggle("Table view", key="hi_table")

    types = EVENT_GROUPS[group]
    shown = [e for e in events if types is None or e.type in types]

    if team_name != "All teams":
        team = next(t for t in tournament.teams if t.name == team_name)
        shown = [e for e in shown if _mentions_team(tournament, e, team)]

    st.caption(f"{len(shown)} of {len(events)} events")

    if not shown:
        st.info("No events match these filters.")
        return

    if as_table:
        st.dataframe(timeline_df(shown), width="stretch", hide_index=True)
    else:
        show_all = len(shown) > PAGE_SIZE and st.toggle(
            f"Show all {len(shown)}", key="hi_show_all"
        )
        with st.container(border=True, key="card-hi-timeline"):
            timeline(shown, limit=None if show_all else PAGE_SIZE)

    st.download_button(
        "Download timeline (CSV)",
        data=export.rows_to_csv(export.timeline_rows(tournament)),
        file_name="timeline.csv",
        mime="text/csv",
        key="hi_download",
        icon=":material/download:",
    )


def _mentions_team(tournament, event, team):
    if event.data.get("team") == team.name:
        return True

    match_id = event.data.get("match_id")
    if match_id is None:
        return False

    match = tournament.get_match(match_id)
    return match is not None and match.involves(team)


# ---------------------------------------------------------------------- #
# Results by matchday
# ---------------------------------------------------------------------- #
def _results_tab(tournament):
    if not tournament.matches:
        st.info("No schedule yet. Generate it in Manage League.")
        return

    for matchday, matches in tournament.matchdays.items():
        played = sum(1 for m in matches if m.is_finished)
        section(f"Matchday {matchday}", f"{played} of {len(matches)} played")
        with st.container(border=True, key=f"card-hi-md-{matchday}"):
            results_list(matches)


# ---------------------------------------------------------------------- #
# Table over time
# ---------------------------------------------------------------------- #
def _table_tab(tournament):
    snapshots = analytics.standings_by_matchday(tournament)

    if len(snapshots) < 2:
        st.info("The table history starts once a matchday has been played.")
        return

    last = snapshots[-1]["matchday"]

    if last > 1:
        matchday = st.slider("Table after matchday", 1, last, last, key="hi_md_slider")
    else:
        matchday = 1
        st.caption("Only matchday 1 has been played so far.")

    snapshot = snapshots[matchday]

    section(f"Standings after matchday {matchday}")
    standings_table(tournament, snapshot["standings"])

    names = [row["team"].name for row in tournament.get_standings()]
    head, pick = st.columns([1.3, 1], vertical_alignment="bottom")
    with head:
        section("Position race", "After every matchday")
    with pick:
        highlight = st.selectbox(
            "Highlight team", names, key="hi_highlight", label_visibility="collapsed"
        )

    with st.container(border=True, key="card-hi-race"):
        st.altair_chart(
            charts.position_race(analytics.position_history_rows(tournament), highlight),
            width="stretch",
            theme=None,
        )


# ---------------------------------------------------------------------- #
# Trends
# ---------------------------------------------------------------------- #
def _trends_tab(tournament):
    summary = analytics.season_summary(tournament)

    if not summary["played"]:
        st.info("Trends appear after the first result.")
        return

    biggest = summary["biggest_win"]
    highest = summary["highest_scoring"]
    stat_row([
        {"label": "Goals per match", "value": summary["goals_per_match"],
         "note": f"{summary['goals']} goals in {summary['played']} matches", "icon_name": "goal"},
        {"label": "Biggest win", "value": _score(biggest) if biggest else "–",
         "note": _fixture(biggest) if biggest else "No match decided yet", "icon_name": "trophy"},
        {"label": "Highest-scoring", "value": _score(highest) if highest else "–",
         "note": _fixture(highest) if highest else "", "icon_name": "flame"},
        {"label": "Cards", "value": summary["yellow_cards"] + summary["red_cards"],
         "note": f"{summary['yellow_cards']} yellow, {summary['red_cards']} red",
         "icon_name": "rectangle-vertical"},
    ])

    left, right = st.columns(2, gap="large")
    with left:
        section("Goals per matchday")
        with st.container(border=True, key="card-hi-goals"):
            st.altair_chart(
                charts.goals_per_matchday(analytics.goals_by_matchday(tournament)),
                width="stretch",
                theme=None,
            )
    with right:
        section("How matches ended", "Share of finished matches")
        with st.container(border=True, key="card-hi-outcomes"):
            st.altair_chart(
                charts.results_breakdown(analytics.results_breakdown(tournament)),
                width="stretch",
                theme=None,
            )

    discipline = analytics.discipline_table(tournament)
    if discipline:
        left, right = st.columns(2, gap="large")
        with left:
            section("Cards by team")
            rows = _cards_by_team(tournament)
            with st.container(border=True, key="card-hi-cards"):
                st.altair_chart(charts.cards_by_team(rows), width="stretch", theme=None)
        with right:
            section("Discipline", "Players with at least one card")
            st.dataframe(discipline_df(discipline), width="stretch", hide_index=True)


def _cards_by_team(tournament):
    rows = []
    for team in tournament.teams:
        stats = analytics.team_stats(tournament, team)
        if stats["yellow_cards"] or stats["red_cards"]:
            rows.append({"team": team.name, "yellow": stats["yellow_cards"], "red": stats["red_cards"]})
    return rows


def _score(match):
    return f"{match.score[0]}–{match.score[1]}"


def _fixture(match):
    return f"{match.team1.name} v {match.team2.name}, matchday {match.matchday}"
