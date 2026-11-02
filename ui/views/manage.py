"""Manage League: register / remove teams, generate fixtures, session tools."""

import streamlit as st

from league import Team, Tournament, build_sample_tournament
from ui.components import header, section
from ui.helpers import team_label, teams_df
from ui.state import DEFAULT_TOURNAMENT_NAME, run_action, set_tournament


def render(tournament):
    header(
        "LEAGUE ADMINISTRATION",
        "Manage League",
        "Register clubs and create the round-robin schedule.",
    )

    section("Register a team")
    _register_team(tournament)

    st.divider()
    section("Generate fixture schedule")
    _generate_schedule(tournament)

    st.divider()
    section("Current teams")
    _current_teams(tournament)

    st.divider()
    section("Session tools")
    _session_tools()


# ---------------------------------------------------------------------- #
# Sections
# ---------------------------------------------------------------------- #
def _register_team(tournament):
    if tournament.schedule_generated:
        st.info("The schedule has been generated, so team registration is closed.")
        return

    with st.form("register_team_form", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            team_id = st.text_input("Team ID", placeholder="e.g. RM")
        with c2:
            team_name = st.text_input("Team name", placeholder="e.g. Real Madrid")

        if st.form_submit_button("＋ Register team", type="primary"):
            run_action(
                lambda: _register(tournament, team_id, team_name),
                lambda team: f"{team.name} registered successfully.",
                "Could not register team",
            )


def _register(tournament, team_id, team_name):
    team = Team(team_id, team_name)
    tournament.register_team(team)
    return team


def _generate_schedule(tournament):
    st.write(
        "Creates a single round-robin schedule: every pair of active teams "
        "plays once."
    )

    active = len(tournament.active_teams)

    if tournament.schedule_generated:
        st.success(f"Schedule generated: {len(tournament.matches)} matches.")
        return

    if active < 2:
        st.caption(f"{active} active team(s) registered. At least 2 are required.")

    if st.button("⚽ Generate schedule", type="primary", disabled=active < 2):
        run_action(
            tournament.generate_schedule,
            lambda matches: f"Schedule generated: {len(matches)} matches.",
            "Could not generate schedule",
        )


def _current_teams(tournament):
    if not tournament.teams:
        st.caption("No teams have been registered yet.")
        return

    st.dataframe(teams_df(tournament.teams), width="stretch", hide_index=True)

    if tournament.schedule_generated:
        st.caption("Teams cannot be removed after the schedule is generated.")
        return

    options = {team_label(t): t for t in tournament.teams}
    c1, c2 = st.columns([3, 1])

    with c1:
        selected = st.selectbox("Remove a team", list(options), key="remove_team_pick")
    with c2:
        st.write("")
        st.write("")
        if st.button("Remove team", key="remove_team_btn"):
            team = options[selected]
            run_action(
                lambda: tournament.unregister_team(team.id),
                f"{team.name} was removed from the tournament.",
                "Could not remove team",
            )


def _session_tools():
    st.warning(
        "These tools replace the tournament held in this running Streamlit "
        "session. Nothing is stored outside the session."
    )

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("**Start a new tournament**")
        name = st.text_input("Tournament name", value=DEFAULT_TOURNAMENT_NAME)
        if st.button("Start new tournament"):
            run_action(
                lambda: set_tournament(Tournament(name)),
                f"Tournament '{name.strip()}' created.",
                "Could not create tournament",
            )

    with c2:
        st.markdown("**Load sample league**")
        st.caption("Three clubs with players, ready for schedule generation.")
        if st.button("Load sample league"):
            run_action(
                lambda: set_tournament(build_sample_tournament()),
                "Sample league loaded.",
                "Could not load sample league",
            )
