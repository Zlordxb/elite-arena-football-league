"""Fixtures: matchday by matchday, kick-off to full time."""

import streamlit as st

from league import MAX_MATCH_MINUTE, CardType, MatchStatus
from ui.components import empty_state, fixture_header, page_header, section, timeline
from ui.components import render as render_html
from ui.helpers import cards_df, player_label, result_text
from ui.state import nav_button, run_action

STATUS_FILTERS = ("All",) + MatchStatus.ALL
MAX_GOALS = 99
ALL_MATCHDAYS = "All"


def render(tournament):
    page_header(
        "Fixtures & results",
        "Start matches, record cards and enter final scores.",
        icon_name="calendar-days",
    )

    if not tournament.matches:
        empty_state(
            "No fixtures yet",
            "Generate the schedule in Manage League once at least two teams are registered.",
            icon_name="calendar-days",
        )
        nav_button("Go to Manage League", "Manage League", key="fx_to_manage", kind="primary")
        return

    matchday_filter, status_filter = _filters(tournament)

    shown_any = False
    for matchday, matches in tournament.matchdays.items():
        if matchday_filter != ALL_MATCHDAYS and matchday != matchday_filter:
            continue

        visible = [m for m in matches if status_filter == "All" or m.status == status_filter]
        if not visible:
            continue

        shown_any = True
        played = sum(1 for m in matches if m.is_finished)
        section(f"Matchday {matchday}", f"{played} of {len(matches)} played")

        for match in visible:
            _render_match(tournament, match)

    if not shown_any:
        st.info("No matches match the current filters.")


def _filters(tournament):
    options = [ALL_MATCHDAYS] + list(tournament.matchdays)
    default = tournament.current_matchday or ALL_MATCHDAYS

    left, right = st.columns([3, 1], vertical_alignment="bottom")
    with left:
        picked = st.segmented_control(
            "Matchday",
            options,
            default=default,
            key="fx_matchday",
            format_func=lambda v: v if v == ALL_MATCHDAYS else f"MD {v}",
        )
    with right:
        status = st.selectbox("Status", STATUS_FILTERS, key="fx_status")

    return (picked if picked is not None else ALL_MATCHDAYS), status


# ---------------------------------------------------------------------- #
# One fixture
# ---------------------------------------------------------------------- #
def _render_match(tournament, match):
    with st.container(border=True, key=f"card-match-{match.match_id}"):
        render_html(fixture_header(match))

        if match.is_upcoming:
            _upcoming_controls(tournament, match)
        elif match.is_live:
            _live_controls(tournament, match)
        else:
            _match_report(match)


def _upcoming_controls(tournament, match):
    inactive = [t.name for t in match.teams if not t.is_active]

    if inactive:
        st.caption(f"Cannot start: {', '.join(inactive)} inactive. Reactivate in Teams & Players.")

    if st.button(
        "Kick off",
        key=f"start_{match.match_id}",
        type="primary",
        disabled=bool(inactive),
        icon=":material/play_arrow:",
    ):
        run_action(
            lambda: tournament.start_match(match.match_id),
            f"Match {match.match_id} is live.",
            "Could not start match",
        )


def _live_controls(tournament, match):
    left, right = st.columns(2, gap="large")

    with left:
        _cards_form(tournament, match)

    with right:
        _finish_form(tournament, match)

    if match.cards:
        st.caption("Cards so far")
        st.dataframe(cards_df(match), width="stretch", hide_index=True)


def _cards_form(tournament, match):
    mid = match.match_id
    players = match.team1.players + match.team2.players

    with st.form(f"card_{mid}"):
        st.markdown("**Record a card**")
        st.caption("Two yellows send the player off. Banned players cannot be booked.")

        if not players:
            st.info("Neither team has registered players yet.")
            st.form_submit_button("Record card", disabled=True)
            return

        options = {player_label(p): p for p in players}
        selected = st.selectbox("Player", list(options), key=f"card_player_{mid}")
        c1, c2 = st.columns([1.3, 1])
        with c1:
            card_type = st.radio(
                "Card", CardType.ALL, horizontal=True, format_func=str.title, key=f"card_type_{mid}"
            )
        with c2:
            minute = st.number_input(
                "Minute (optional)", min_value=1, max_value=MAX_MATCH_MINUTE, value=None,
                step=1, key=f"card_minute_{mid}",
            )

        if st.form_submit_button("Record card", width="stretch", icon=":material/style:"):
            player = options[selected]
            minute = int(minute) if minute is not None else None
            run_action(
                lambda: tournament.record_card(mid, player.id, card_type, minute),
                lambda _: (
                    f"{player.name} has been sent off."
                    if match.is_sent_off(player)
                    else f"{card_type.title()} card recorded for {player.name}."
                ),
                "Could not record card",
            )


def _finish_form(tournament, match):
    mid = match.match_id

    with st.form(f"finish_{mid}"):
        st.markdown("**Final score**")
        st.caption("Saving the score ends the match and updates the table.")
        c1, c2 = st.columns(2)

        with c1:
            score1 = st.number_input(
                f"{match.team1.name} goals",
                min_value=0, max_value=MAX_GOALS, step=1, key=f"s1_{mid}",
            )
        with c2:
            score2 = st.number_input(
                f"{match.team2.name} goals",
                min_value=0, max_value=MAX_GOALS, step=1, key=f"s2_{mid}",
            )

        if st.form_submit_button("Save final score", type="primary", width="stretch",
                                 icon=":material/sports_score:"):
            run_action(
                lambda: tournament.finish_match(mid, int(score1), int(score2)),
                f"Full time in match {mid}: {match.team1.name} {int(score1)} - {int(score2)} "
                f"{match.team2.name}.",
                "Could not finish match",
            )


def _match_report(match):
    details = match.get_match_details()

    with st.expander("Match report"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Result", result_text(match))
        c2.metric("Yellow cards", details["yellow_cards"])
        c3.metric("Red cards", details["red_cards"])

        left, right = st.columns([1, 1], gap="large")
        with left:
            st.caption("Match timeline")
            timeline(match.events.events, clock_only=True)
        with right:
            if match.cards:
                st.caption("Cards")
                st.dataframe(cards_df(match), width="stretch", hide_index=True)
            else:
                st.caption("No cards were shown in this match.")
