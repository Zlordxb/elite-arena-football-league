"""Standings: the official table, goals and the form guide."""

from html import escape as esc

import streamlit as st

from league import analytics
from ui import charts
from ui.components import (
    empty_state,
    form_pills,
    page_header,
    pill,
    section,
    standings_table,
    team_badge,
)
from ui.components import render as render_html
from ui.helpers import streak_text
from ui.state import nav_button


def render(tournament):
    page_header(
        "Standings",
        "Three points for a win, one for a draw. Ties break on goal difference, then goals scored.",
        aside=pill(tournament.phase, "gold" if tournament.is_complete else ""),
        icon_name="list-ordered",
    )

    if not tournament.teams:
        empty_state("No teams yet", "Register teams in Manage League and the table appears here.",
                    icon_name="list-ordered")
        nav_button("Go to Manage League", "Manage League", key="st_to_manage", kind="primary")
        return

    standings = tournament.get_standings()

    if tournament.is_complete:
        champion = standings[0]["team"]
        st.success(f"Season complete. Champion: **{champion.name}**")

    standings_table(tournament, standings)

    if not tournament.finished_matches:
        st.caption("The table fills in as results are saved in Fixtures.")
        return

    left, right = st.columns(2, gap="large")
    with left:
        section("Goals scored and conceded")
        with st.container(border=True, key="card-st-goals"):
            st.altair_chart(charts.goals_for_against(standings), width="stretch", theme=None)
    with right:
        section("Goal difference")
        with st.container(border=True, key="card-st-gd"):
            st.altair_chart(charts.goal_difference_bar(standings), width="stretch", theme=None)

    section("Form guide", "Most recent result on the right")
    _form_guide(tournament, standings)


def _form_guide(tournament, standings):
    rows = []
    for row in standings:
        stats = analytics.team_stats(tournament, row["team"])
        rows.append(
            "<tr>"
            f'<td class="rank">{row["rank"]}</td>'
            f'<td class="team">{team_badge(row["team"], 24)}</td>'
            f"<td>{form_pills(stats['form'])}</td>"
            f'<td class="num">{esc(streak_text(stats["streak"]))}</td>'
            f'<td class="num">{stats["unbeaten_run"]}</td>'
            f'<td class="num">{stats["clean_sheets"]}</td>'
            f'<td class="num">{stats["yellow_cards"]}</td>'
            f'<td class="num">{stats["red_cards"]}</td>'
            "</tr>"
        )

    render_html(
        '<div class="ea-table-wrap"><table class="ea-table"><thead><tr>'
        "<th></th><th class='left'>Team</th><th class='left'>Last 5</th><th>Streak</th>"
        "<th>Unbeaten</th><th>Clean sheets</th><th>Yellow</th><th>Red</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )
