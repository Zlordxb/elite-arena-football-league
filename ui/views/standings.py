"""Standings: the league table as computed by Tournament.get_standings()."""

import streamlit as st

from ui.components import header
from ui.helpers import standings_df

COLUMN_CONFIG = {
    "Pos": st.column_config.NumberColumn("POS", format="%d"),
    "Team": st.column_config.TextColumn("TEAM"),
    "P": st.column_config.NumberColumn("P", help="Played"),
    "W": st.column_config.NumberColumn("W", help="Won"),
    "D": st.column_config.NumberColumn("D", help="Drawn"),
    "L": st.column_config.NumberColumn("L", help="Lost"),
    "GF": st.column_config.NumberColumn("GF", help="Goals for"),
    "GA": st.column_config.NumberColumn("GA", help="Goals against"),
    "GD": st.column_config.NumberColumn("GD", help="Goal difference"),
    "PTS": st.column_config.NumberColumn("PTS", help="Points"),
}


def render(tournament):
    header(
        "LEAGUE TABLE",
        "Official Standings",
        "The table is calculated from completed match results using your "
        "Tournament class.",
    )

    if not tournament.teams:
        st.info(
            "Your league table will appear here after teams are registered. "
            "Results update the table automatically."
        )
        return

    df = standings_df(tournament)

    with st.container(border=True):
        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            height=min(600, 48 + 38 * len(df)),
            column_config=COLUMN_CONFIG,
        )

    st.caption(
        "Ranking: points, then goal difference, then goals scored. "
        "The UI does not calculate league points separately."
    )

    if tournament.is_complete:
        champion = tournament.get_standings()[0]["team"]
        st.success(f"🏆 Season complete. Champion: **{champion.name}**")
