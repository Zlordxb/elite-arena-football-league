"""Dashboard: season overview, recent results and the current table."""

import streamlit as st

from league import MatchStatus
from ui.components import header, muted, section, stat_card
from ui.helpers import match_counts, score_text, standings_df

RECENT_RESULTS_LIMIT = 5


def render(tournament):
    header(
        "SEASON CONTROL CENTER",
        "League Dashboard",
        "Your tournament at a glance. Fixtures, results and standings in one place.",
    )

    counts = match_counts(tournament)
    _stat_cards(tournament, counts)

    section("Matchday overview")
    left, right = st.columns([1.35, 1], gap="large")

    with left:
        _recent_results(tournament)

    with right:
        _season_progress(counts)

    section("Current standings")
    _standings(tournament)


def _stat_cards(tournament, counts):
    cols = st.columns(4, gap="medium")
    metrics = [
        ("REGISTERED TEAMS", len(tournament.teams), "Teams in this league"),
        ("TOTAL FIXTURES", counts["total"], "Scheduled matchups"),
        ("COMPLETED", counts["finished"], "Matches with final scores"),
        ("LIVE NOW", counts["live"], "Currently in progress"),
    ]

    for col, (label, value, note) in zip(cols, metrics):
        with col:
            stat_card(label, value, note.upper())


def _recent_results(tournament):
    with st.container(border=True):
        st.markdown("**Recent results**")

        completed = tournament.get_matches_by_status(MatchStatus.FINISHED)

        if not completed:
            st.info(
                "No completed matches yet. Go to Fixtures to start a match "
                "and enter its result."
            )
            return

        for match in completed[-RECENT_RESULTS_LIMIT:][::-1]:
            st.markdown(
                f"**{match.team1.name}**　`{score_text(match)}`　"
                f"**{match.team2.name}**"
            )
            muted(f"Match #{match.match_id} · Finished")
            st.markdown("---")


def _season_progress(counts):
    with st.container(border=True):
        st.markdown("**Season progress**")

        total = counts["total"]
        progress = (counts["finished"] / total) if total else 0.0

        st.progress(
            progress,
            text=f"{counts['finished']} of {total} fixtures completed",
        )
        st.markdown(f"- **Upcoming:** {counts['upcoming']}")
        st.markdown(f"- **Live:** {counts['live']}")
        st.markdown(f"- **Finished:** {counts['finished']}")


def _standings(tournament):
    if not tournament.teams:
        st.info(
            "Register at least two teams and generate the fixture schedule "
            "to begin."
        )
        return

    df = standings_df(tournament)
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        height=min(360, 44 + 36 * len(df)),
    )
