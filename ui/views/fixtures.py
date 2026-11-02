"""Fixtures: start matches, record cards, enter final scores."""

import streamlit as st

from league import CardType, MatchStatus
from ui.components import header, right_muted, scoreline, status_pill
from ui.helpers import cards_df, player_label, result_text, score_text
from ui.state import run_action

STATUS_FILTERS = ("All",) + MatchStatus.ALL
MAX_GOALS = 99


def render(tournament):
    header(
        "MATCH CENTER",
        "Fixtures & Results",
        "Follow every matchup and update results as your tournament progresses.",
    )

    if not tournament.matches:
        st.warning(
            "No fixtures yet. Open **Manage League** and generate the schedule "
            "after registering at least two teams."
        )
        return

    status_filter = st.selectbox("Filter matches", STATUS_FILTERS)
    shown = [
        m for m in tournament.matches
        if status_filter == "All" or m.status == status_filter
    ]

    if not shown:
        st.info(f"No {status_filter.lower()} matches right now.")
        return

    for match in shown:
        _render_match(match)


# ---------------------------------------------------------------------- #
# One fixture card
# ---------------------------------------------------------------------- #
def _render_match(match):
    mid = match.match_id

    with st.container(border=True):
        top = st.columns([1.2, 2.2, 1.2])

        with top[0]:
            st.caption(f"MATCH #{mid}")
            status_pill(match.status)

        with top[1]:
            scoreline(match, score_text(match))

        with top[2]:
            right_muted(result_text(match) or "ELITE ARENA")

        if match.is_upcoming:
            _upcoming_controls(match)
        elif match.is_live:
            _live_controls(match)
        else:
            _finished_details(match)


def _upcoming_controls(match):
    inactive = [t.name for t in match.teams if not t.is_active]

    if inactive:
        st.caption(f"Cannot start: inactive team(s) {', '.join(inactive)}.")

    if st.button(
        "▶ Start match",
        key=f"start_{match.match_id}",
        type="primary",
        disabled=bool(inactive),
    ):
        run_action(
            match.start_match,
            f"Match #{match.match_id} is now live.",
            "Could not start match",
        )


def _live_controls(match):
    left, right = st.columns(2, gap="large")

    with left:
        _cards_form(match)

    with right:
        _finish_form(match)

    if match.yellow_cards or match.red_cards:
        st.caption("Cards shown so far")
        st.dataframe(cards_df(match), width="stretch", hide_index=True)


def _cards_form(match):
    mid = match.match_id
    players = match.team1.players + match.team2.players

    with st.form(f"card_{mid}"):
        st.caption("Record a card (two yellows send the player off).")

        if not players:
            st.info("Neither team has registered players yet.")
            st.form_submit_button("Record card", disabled=True)
            return

        options = {player_label(p): p for p in players}
        selected = st.selectbox("Player", list(options), key=f"card_player_{mid}")
        card_type = st.radio(
            "Card",
            CardType.ALL,
            horizontal=True,
            format_func=str.title,
            key=f"card_type_{mid}",
        )

        if st.form_submit_button("Record card", width="stretch"):
            player = options[selected]
            run_action(
                lambda: match.add_card(player, card_type),
                lambda _: (
                    f"{player.name} has been sent off."
                    if match.is_sent_off(player)
                    else f"{card_type.title()} card recorded for {player.name}."
                ),
                "Could not record card",
            )


def _finish_form(match):
    mid = match.match_id

    with st.form(f"finish_{mid}"):
        st.caption("Enter the final score to finish this match.")
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

        if st.form_submit_button("Save final result", type="primary", width="stretch"):
            run_action(
                lambda: match.finish_match(int(score1), int(score2)),
                f"Result saved for match #{mid}. Standings have been recalculated.",
                "Could not finish match",
            )


def _finished_details(match):
    with st.expander("Match details"):
        details = match.get_match_details()
        c1, c2, c3 = st.columns(3)
        c1.metric("Result", result_text(match))
        c2.metric("Yellow cards", details["yellow_cards"])
        c3.metric("Red cards", details["red_cards"])

        if match.yellow_cards or match.red_cards:
            st.dataframe(cards_df(match), width="stretch", hide_index=True)
        else:
            st.caption("No cards were shown in this match.")
