"""Manage League: register / remove teams, generate fixtures, branding, session tools."""

import streamlit as st

from league import Team, Tournament, build_sample_tournament
from ui import assets
from ui.components import club_cards, empty_state, page_header, phase_pill, section
from ui.helpers import team_label
from ui.state import DEFAULT_TOURNAMENT_NAME, flash, nav_button, run_action, set_tournament


def render(tournament):
    page_header(
        "Manage league",
        "Register clubs, build the round-robin schedule, or start over.",
        aside=phase_pill(tournament.phase),
        icon_name="sliders-horizontal",
    )

    left, right = st.columns(2, gap="large")
    with left:
        section("Register a team")
        _register_team(tournament)
    with right:
        section("Schedule")
        _generate_schedule(tournament)

    section("Registered teams", f"{len(tournament.teams)} teams")
    _current_teams(tournament)

    section("Branding", "Dashboard backdrop")
    _branding()

    section("Session")
    _session_tools()


# ---------------------------------------------------------------------- #
# Sections
# ---------------------------------------------------------------------- #
def _register_team(tournament):
    if tournament.schedule_generated:
        st.info("Registration closed: the schedule has been generated.")
        return

    with st.form("register_team_form", clear_on_submit=True):
        c1, c2 = st.columns([1, 2])

        with c1:
            team_id = st.text_input("Team ID", placeholder="e.g. RM")
        with c2:
            team_name = st.text_input("Team name", placeholder="e.g. Real Madrid")

        if st.form_submit_button("Register team", type="primary", icon=":material/add:"):
            run_action(
                lambda: _register(tournament, team_id, team_name),
                lambda team: f"{team.name} registered.",
                "Could not register team",
            )


def _register(tournament, team_id, team_name):
    team = Team(team_id, team_name)
    tournament.register_team(team)
    return team


def _generate_schedule(tournament):
    active = len(tournament.active_teams)

    if tournament.schedule_generated:
        st.success(
            f"{len(tournament.matches)} matches over {tournament.total_matchdays} matchdays."
        )
        nav_button("Open fixtures", "Fixtures", key="mg_to_fixtures")
        return

    st.write(
        "Single round-robin: every pair of active teams plays once, and every team "
        "plays at most once per matchday. Registration closes once the schedule exists."
    )

    if active < 2:
        st.caption(f"{active} active team(s) registered. At least 2 are required.")

    if st.button("Generate schedule", type="primary", disabled=active < 2, key="mg_generate",
                 icon=":material/calendar_month:"):
        run_action(
            tournament.generate_schedule,
            lambda matches: f"Schedule generated: {len(matches)} matches.",
            "Could not generate schedule",
        )


def _current_teams(tournament):
    if not tournament.teams:
        empty_state("No teams registered", "Use the form above to add the first team.", icon_name="shield")
        return

    club_cards(tournament.teams)

    if tournament.schedule_generated:
        st.caption("Teams cannot be removed after the schedule is generated.")
        return

    options = {team_label(t): t for t in tournament.teams}
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")

    with c1:
        selected = st.selectbox("Remove a team", list(options), key="remove_team_pick")
    with c2:
        if st.button("Remove team", key="remove_team_btn", width="stretch", icon=":material/delete:"):
            team = options[selected]
            run_action(
                lambda: tournament.unregister_team(team.id),
                f"{team.name} was removed from the tournament.",
                "Could not remove team",
            )


def _branding():
    st.caption(
        "A stadium photo behind the dashboard hero. Upload one for this session, or save it "
        "permanently as assets/hero.jpg (png and webp work too). Without a photo the hero "
        "shows a drawn pitch."
    )
    left, right = st.columns([1.4, 1], gap="large")

    with left:
        with st.form("hero_form", clear_on_submit=True):
            uploaded = st.file_uploader(
                "Hero image (up to 1.5 MB)",
                type=["png", "jpg", "jpeg", "webp"],
                key=assets.uploader_key("hero_upload"),
            )
            if st.form_submit_button("Save backdrop", type="primary", icon=":material/upload:"):
                run_action(
                    lambda: assets.save_upload("hero", None, uploaded),
                    lambda name: f"Backdrop saved ({name}).",
                    "Could not save backdrop",
                )

    with right:
        if assets.has_upload("hero"):
            st.success("A session backdrop is in use.")
            if st.button("Remove backdrop", key="rm_hero", icon=":material/delete:"):
                assets.remove_upload("hero")
                flash("success", "Backdrop removed.")
                st.rerun()
        elif assets.has_custom_image("hero"):
            st.info("Using assets/hero image from disk.")
        else:
            st.caption("No photo set: the drawn pitch is shown.")


def _session_tools():
    st.caption(
        "These replace the tournament held in this browser session. "
        "Nothing is stored outside the session."
    )

    c1, c2 = st.columns(2, gap="large")

    with c1:
        with st.container(border=True, key="card-mg-new"):
            st.markdown("**Start a new tournament**")
            name = st.text_input("Tournament name", value=DEFAULT_TOURNAMENT_NAME, key="mg_new_name")
            if st.button("Start new tournament", key="mg_new", icon=":material/refresh:"):
                run_action(
                    lambda: set_tournament(Tournament(name)),
                    f"Tournament '{name.strip()}' created.",
                    "Could not create tournament",
                )

    with c2:
        with st.container(border=True, key="card-mg-sample"):
            st.markdown("**Load the sample league**")
            st.caption("Three clubs with players, ready for schedule generation.")
            if st.button("Load sample league", key="mg_sample", icon=":material/download:"):
                run_action(
                    lambda: set_tournament(build_sample_tournament()),
                    "Sample league loaded.",
                    "Could not load sample league",
                )
