"""Teams & Players: squads, identity (crest, colour, photos), bans and history."""

import streamlit as st

from league import PLAYER_ROLES, HumanPlayer, analytics
from ui import assets
from ui.components import (
    club_identity,
    empty_state,
    page_header,
    player_cards,
    section,
    stat_row,
    timeline,
)
from ui.helpers import player_label, plural, streak_text, team_label
from ui.state import flash, nav_button, run_action


def render(tournament):
    page_header(
        "Teams & players",
        "Squads, availability and each club's season so far.",
        icon_name="users",
    )

    if not tournament.teams:
        empty_state("No teams yet", "Register teams in Manage League, then build their squads here.")
        nav_button("Go to Manage League", "Manage League", key="tm_to_manage", kind="primary")
        return

    team = _select_team(tournament.teams)
    stats = analytics.team_stats(tournament, team)

    club_identity(team, stats)
    _overview(tournament, team, stats)

    with st.expander("Club identity: crest and colour"):
        _identity_editor(team)

    section("Squad", f"{len(team.players)} players, {len(team.banned_players)} banned")
    _roster(team)

    left, right = st.columns(2, gap="large")
    with left:
        section("Add a player")
        _add_player_form(tournament, team)
    with right:
        section("Player actions")
        _player_actions(tournament, team)

    section("Club history", "Most recent first")
    _team_history(tournament, team)


# ---------------------------------------------------------------------- #
# Sections
# ---------------------------------------------------------------------- #
def _select_team(teams):
    options = {team_label(t): t for t in teams}
    selected = st.selectbox("Team", list(options), key="tm_team")
    return options[selected]


def _overview(tournament, team, stats):
    stat_row([
        {"label": "Position", "value": stats["rank"], "unit": f"of {len(tournament.teams)}",
         "note": plural(stats["points"], "point"), "icon_name": "trophy",
         "tone": "gold" if stats["rank"] == 1 and stats["played"] else ""},
        {"label": "Record", "value": f"{stats['won']}-{stats['drawn']}-{stats['lost']}",
         "note": f"{stats['played']} played, W-D-L", "icon_name": "list-ordered"},
        {"label": "Goals", "value": f"{stats['goals_for']}:{stats['goals_against']}",
         "note": f"{stats['goal_difference']:+d} difference, {plural(stats['clean_sheets'], 'clean sheet')}",
         "icon_name": "goal"},
        {"label": "Streak", "value": streak_text(stats["streak"]),
         "note": f"{stats['unbeaten_run']} unbeaten", "icon_name": "flame"},
        {"label": "Cards", "value": stats["yellow_cards"] + stats["red_cards"],
         "note": f"{stats['yellow_cards']} yellow, {stats['red_cards']} red",
         "icon_name": "rectangle-vertical"},
    ])

    _, right = st.columns([2, 1])
    with right:
        if team.is_active:
            if st.button("Deactivate team", key=f"deactivate_{team.id}", width="stretch",
                         icon=":material/pause_circle:"):
                run_action(
                    lambda: tournament.set_team_active(team.id, False),
                    f"{team.name} is now inactive.",
                    "Could not deactivate team",
                )
        else:
            if st.button("Activate team", key=f"activate_{team.id}", type="primary", width="stretch",
                         icon=":material/play_circle:"):
                run_action(
                    lambda: tournament.set_team_active(team.id, True),
                    f"{team.name} is active again.",
                    "Could not activate team",
                )


def _identity_editor(team):
    st.caption(
        "Upload a crest for this session, or drop a file in assets/teams/ named after the "
        f"team ID ({team.id}) or its slug ({assets.slug(team.name)}) to keep it permanently."
    )
    left, right = st.columns([1, 1.4], gap="large")

    with left:
        color = st.color_picker("Crest colour", value=assets.team_color(team), key=f"color_{team.id}")
        assets.set_team_color(team, color)

        if assets.has_upload("teams", team.id):
            if st.button("Remove uploaded crest", key=f"rm_logo_{team.id}", icon=":material/delete:"):
                assets.remove_upload("teams", team.id)
                flash("success", f"Crest removed for {team.name}.")
                st.rerun()

    with right:
        with st.form(f"logo_form_{team.id}", clear_on_submit=True):
            uploaded = st.file_uploader(
                "Crest image (png, jpg, webp or svg, up to 1.5 MB)",
                type=list(assets.IMAGE_TYPES),
                key=assets.uploader_key(f"logo_{team.id}"),
            )
            if st.form_submit_button("Save crest", type="primary", icon=":material/upload:"):
                run_action(
                    lambda: assets.save_upload("teams", team.id, uploaded),
                    lambda name: f"Crest saved for {team.name} ({name}).",
                    "Could not save crest",
                )


def _roster(team):
    if not team.players:
        st.info("This team has no players yet. Add the first one below.")
        return

    player_cards(team.players)


def _add_player_form(tournament, team):
    with st.form(f"add_player_{team.id}", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            player_id = st.text_input("Player ID", placeholder="e.g. 101")
        with c2:
            name = st.text_input("Player name", placeholder="e.g. Player One")

        role = st.selectbox("Role", PLAYER_ROLES)

        if st.form_submit_button("Add player", type="primary", icon=":material/person_add:"):
            run_action(
                lambda: tournament.add_player_to_team(
                    team.id, HumanPlayer(player_id, name, role)
                ),
                lambda player: f"{player.name} joined {team.name}.",
                "Could not add player",
            )


def _player_actions(tournament, team):
    if not team.players:
        st.caption("Add a player first to ban, unban or remove players.")
        return

    options = {player_label(p, with_team=False): p for p in team.players}
    selected = st.selectbox("Player", list(options), key=f"player_pick_{team.id}")
    player = options[selected]

    b1, b2 = st.columns(2)

    with b1:
        if player.is_banned:
            if st.button("Unban player", key=f"unban_{team.id}_{player.id}", type="primary",
                         width="stretch", icon=":material/check_circle:"):
                run_action(
                    lambda: tournament.unban_player(player.id),
                    f"{player.name} is available again.",
                    "Could not unban player",
                )
        else:
            if st.button("Ban player", key=f"ban_{team.id}_{player.id}", width="stretch",
                         icon=":material/block:"):
                run_action(
                    lambda: tournament.ban_player(player.id),
                    f"{player.name} has been banned.",
                    "Could not ban player",
                )

    with b2:
        if st.button("Remove from team", key=f"remove_{team.id}_{player.id}", width="stretch",
                     icon=":material/person_remove:"):
            run_action(
                lambda: tournament.remove_player(player.id),
                f"{player.name} was removed from {team.name}.",
                "Could not remove player",
            )

    with st.expander("Player photo"):
        st.caption(
            f"Shown on the squad card. Permanent option: assets/players/{player.id}.png"
        )
        with st.form(f"photo_form_{team.id}", clear_on_submit=True):
            uploaded = st.file_uploader(
                "Photo (png, jpg or webp, up to 1.5 MB)",
                type=["png", "jpg", "jpeg", "webp"],
                key=assets.uploader_key(f"photo_{player.id}"),
            )
            if st.form_submit_button("Save photo", icon=":material/upload:"):
                run_action(
                    lambda: assets.save_upload("players", player.id, uploaded),
                    lambda name: f"Photo saved for {player.name}.",
                    "Could not save photo",
                )
        if assets.has_upload("players", player.id):
            if st.button("Remove uploaded photo", key=f"rm_photo_{player.id}", icon=":material/delete:"):
                assets.remove_upload("players", player.id)
                flash("success", f"Photo removed for {player.name}.")
                st.rerun()


def _team_history(tournament, team):
    events = [
        e for e in tournament.get_timeline()
        if _mentions_team(tournament, e, team)
    ]

    if not events:
        st.caption("Nothing recorded for this club yet.")
        return

    with st.container(border=True, key=f"card-team-history-{team.id}"):
        timeline(events, limit=12)


def _mentions_team(tournament, event, team):
    if event.data.get("team") == team.name:
        return True

    match_id = event.data.get("match_id")
    if match_id is None:
        return False

    match = tournament.get_match(match_id)
    return match is not None and match.involves(team)
