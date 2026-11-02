"""Teams & Players: rosters, player registration, bans and team status."""

import streamlit as st

from league import PLAYER_ROLES, HumanPlayer
from ui.components import header, section
from ui.helpers import player_label, players_df, team_label
from ui.state import run_action


def render(tournament):
    header(
        "SQUAD DIRECTORY",
        "Teams & Players",
        "Explore the registered clubs and manage their player rosters.",
    )

    if not tournament.teams:
        st.info("No teams registered yet. Add teams from Manage League.")
        return

    team = _select_team(tournament.teams)

    _team_overview(tournament, team)

    section("Squad roster")
    _roster(team)

    left, right = st.columns(2, gap="large")

    with left:
        section("Add a player")
        _add_player_form(tournament, team)

    with right:
        section("Player actions")
        _player_actions(team)


# ---------------------------------------------------------------------- #
# Sections
# ---------------------------------------------------------------------- #
def _select_team(teams):
    options = {team_label(t): t for t in teams}
    selected = st.selectbox("Select a team", list(options))
    return options[selected]


def _team_overview(tournament, team):
    a, b, c, d = st.columns([1, 1, 1, 1.4])
    a.metric("Players", len(team.players))
    b.metric("Banned", len(team.banned_players))
    c.metric("Team status", "Active" if team.is_active else "Inactive")

    with d:
        st.caption("Team status")
        if team.is_active:
            st.caption("Inactive teams cannot start matches.")
            if st.button("Deactivate team", key=f"deactivate_{team.id}"):
                run_action(
                    lambda: tournament.set_team_active(team.id, False),
                    f"{team.name} is now inactive.",
                    "Could not deactivate team",
                )
        else:
            if st.button("Activate team", key=f"activate_{team.id}", type="primary"):
                run_action(
                    lambda: tournament.set_team_active(team.id, True),
                    f"{team.name} is active again.",
                    "Could not activate team",
                )


def _roster(team):
    if not team.players:
        st.info("This team has no players registered yet.")
        return

    st.dataframe(players_df(team.players), width="stretch", hide_index=True)


def _add_player_form(tournament, team):
    with st.form(f"add_player_{team.id}", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            player_id = st.text_input("Player ID", placeholder="e.g. 101")
        with c2:
            name = st.text_input("Player name", placeholder="e.g. Player One")

        role = st.selectbox("Role", PLAYER_ROLES)

        if st.form_submit_button("＋ Add player", type="primary"):
            run_action(
                lambda: tournament.add_player_to_team(
                    team.id, HumanPlayer(player_id, name, role)
                ),
                lambda player: f"{player.name} joined {team.name}.",
                "Could not add player",
            )


def _player_actions(team):
    if not team.players:
        st.caption("Add a player first to ban, unban or remove players.")
        return

    options = {player_label(p, with_team=False): p for p in team.players}
    selected = st.selectbox("Player", list(options), key=f"player_pick_{team.id}")
    player = options[selected]

    b1, b2 = st.columns(2)

    with b1:
        if player.is_banned:
            if st.button("Unban player", key=f"unban_{team.id}_{player.id}", type="primary"):
                run_action(
                    player.unban,
                    f"{player.name} is available again.",
                    "Could not unban player",
                )
        else:
            if st.button("Ban player", key=f"ban_{team.id}_{player.id}"):
                run_action(
                    player.ban,
                    f"{player.name} has been banned.",
                    "Could not ban player",
                )

    with b2:
        if st.button("Remove from team", key=f"remove_{team.id}_{player.id}"):
            run_action(
                lambda: team.remove_player(player.id),
                f"{player.name} was removed from {team.name}.",
                "Could not remove player",
            )
