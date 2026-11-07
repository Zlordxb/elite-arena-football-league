"""Tools: exports, simulation, head-to-head and team comparison."""

import streamlit as st

from league import analytics, export, simulation
from ui.components import (
    club_identity,
    empty_state,
    head_to_head_card,
    page_header,
    results_list,
    section,
    stat_row,
    tab_bar,
)
from ui.helpers import match_label, streak_text, team_label
from ui.state import get_rng, nav_button, run_action


def render(tournament):
    page_header("Tools", "Export the season, simulate results, and compare clubs.", icon_name="wrench")

    sections = {
        "Export": _export_tab,
        "Simulate": _simulation_tab,
        "Head-to-head": _head_to_head_tab,
        "Compare teams": _compare_tab,
    }
    selected = tab_bar("tools_tabs", list(sections))
    sections[selected](tournament)


# ---------------------------------------------------------------------- #
# Export
# ---------------------------------------------------------------------- #
def _export_tab(tournament):
    slug = "".join(ch if ch.isalnum() else "-" for ch in tournament.name.lower()).strip("-")

    section("Data files", "CSV, one row per record")
    c1, c2, c3 = st.columns(3)
    downloads = [
        (c1, "Standings", export.standings_rows(tournament), "standings"),
        (c2, "Fixtures & results", export.fixtures_rows(tournament), "fixtures"),
        (c3, "Players", export.players_rows(tournament), "players"),
        (c1, "Cards", export.cards_rows(tournament), "cards"),
        (c2, "Timeline", export.timeline_rows(tournament), "timeline"),
    ]
    for col, label, rows, name in downloads:
        with col:
            st.download_button(
                f"{label} (CSV)",
                data=export.rows_to_csv(rows),
                file_name=f"{slug}-{name}.csv",
                mime="text/csv",
                disabled=not rows,
                key=f"dl_{name}",
                width="stretch",
                icon=":material/download:",
            )

    section("Season snapshot")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Full snapshot (JSON)",
            data=export.to_json(tournament),
            file_name=f"{slug}.json",
            mime="application/json",
            key="dl_json",
            width="stretch",
            icon=":material/data_object:",
        )
        st.caption("Teams, players, matches with events and cards, standings and history.")
    with c2:
        report = export.season_report_markdown(tournament)
        st.download_button(
            "Season report (Markdown)",
            data=report,
            file_name=f"{slug}-report.md",
            mime="text/markdown",
            key="dl_report",
            width="stretch",
            icon=":material/description:",
        )
        st.caption("Standings, results by matchday and discipline, ready to share.")

    with st.expander("Preview the season report"):
        st.markdown(report)


# ---------------------------------------------------------------------- #
# Simulation
# ---------------------------------------------------------------------- #
def _simulation_tab(tournament):
    if not tournament.matches:
        empty_state(
            "Nothing to simulate yet",
            "Generate the schedule first. Simulation plays upcoming fixtures with random scores and cards.",
            icon_name="dices",
        )
        nav_button("Go to Manage League", "Manage League", key="sim_to_manage", kind="primary")
        return

    upcoming = [m for m in tournament.matches if m.is_upcoming]
    st.caption(
        "Simulated matches follow every league rule and are recorded in the history "
        "exactly like matches you play by hand."
    )
    with_cards = st.toggle("Include random cards", value=True, key="sim_cards")

    if not upcoming:
        st.success("Every fixture has been played. Start a new tournament from Manage League to play again.")
        return

    rng = get_rng()
    matchday = tournament.current_matchday
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(f"Play matchday {matchday}", type="primary", key="sim_next", width="stretch",
                     icon=":material/casino:"):
            run_action(
                lambda: simulation.simulate_next_matchday(tournament, rng, with_cards),
                lambda played: f"Matchday {matchday} played: {len(played)} matches.",
                "Could not simulate matchday",
            )
    with c2:
        if st.button("Play the whole season", key="sim_season", width="stretch",
                     icon=":material/fast_forward:"):
            run_action(
                lambda: simulation.simulate_season(tournament, rng, with_cards),
                lambda played: f"Season simulated: {len(played)} matches played.",
                "Could not simulate season",
            )
    with c3:
        options = {match_label(m): m for m in upcoming}
        picked = st.selectbox("Single match", list(options), key="sim_pick", label_visibility="collapsed")
        if st.button("Play this match", key="sim_one", width="stretch", icon=":material/sports_soccer:"):
            match = options[picked]
            run_action(
                lambda: simulation.simulate_match(tournament, match, rng, with_cards),
                lambda m: f"Full time: {m.team1.name} {m.score[0]} - {m.score[1]} {m.team2.name}.",
                "Could not simulate match",
            )

    st.caption(f"{len(upcoming)} upcoming fixtures remain.")


# ---------------------------------------------------------------------- #
# Head-to-head
# ---------------------------------------------------------------------- #
def _pick_two_teams(tournament, prefix):
    if len(tournament.teams) < 2:
        st.info("Register at least two teams to compare them.")
        return None, None

    options = {team_label(t): t for t in tournament.teams}
    labels = list(options)
    c1, c2 = st.columns(2)
    with c1:
        a = st.selectbox("First team", labels, index=0, key=f"{prefix}_a")
    with c2:
        b = st.selectbox("Second team", labels, index=1, key=f"{prefix}_b")

    if a == b:
        st.warning("Pick two different teams.")
        return None, None

    return options[a], options[b]


def _head_to_head_tab(tournament):
    team_a, team_b = _pick_two_teams(tournament, "h2h")
    if team_a is None:
        return

    record = analytics.head_to_head(tournament, team_a, team_b)
    head_to_head_card(record)

    if record["matches"]:
        section("Meetings this season")
        with st.container(border=True, key="card-h2h-matches"):
            results_list(record["matches"])
    else:
        st.caption("These teams are not scheduled against each other yet.")


# ---------------------------------------------------------------------- #
# Compare teams
# ---------------------------------------------------------------------- #
def _compare_tab(tournament):
    team_a, team_b = _pick_two_teams(tournament, "cmp")
    if team_a is None:
        return

    for team in (team_a, team_b):
        stats = analytics.team_stats(tournament, team)
        club_identity(team, stats)
        stat_row([
            {"label": "Points", "value": stats["points"], "note": f"{stats['played']} played",
             "icon_name": "trophy", "tone": "gold" if stats["rank"] == 1 and stats["played"] else ""},
            {"label": "Record", "value": f"{stats['won']}-{stats['drawn']}-{stats['lost']}", "note": "W-D-L",
             "icon_name": "list-ordered"},
            {"label": "Goals", "value": f"{stats['goals_for']}:{stats['goals_against']}",
             "note": f"{stats['goal_difference']:+d} difference", "icon_name": "goal"},
            {"label": "Clean sheets", "value": stats["clean_sheets"],
             "note": f"{stats['unbeaten_run']} unbeaten, streak {streak_text(stats['streak'])}",
             "icon_name": "shield-check"},
            {"label": "Cards", "value": stats["yellow_cards"] + stats["red_cards"],
             "note": f"{stats['yellow_cards']} yellow, {stats['red_cards']} red",
             "icon_name": "rectangle-vertical"},
        ])
