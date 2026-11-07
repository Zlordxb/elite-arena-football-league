"""Sidebar: brand, navigation and a compact season card."""

from html import escape as esc

import streamlit as st

from league import MatchStatus
from ui.components import phase_pill, render
from ui.icons import NAV_ICONS, icon
from ui.state import NAV_KEY, PAGES


def render_sidebar(tournament):
    with st.sidebar:
        render(
            f'<div class="ea-brand">{icon("trophy")}<span>Elite Arena'
            "<small>Football league manager</small></span></div>"
        )

        page = st.radio(
            "Navigation",
            PAGES,
            key=NAV_KEY,
            format_func=lambda name: f"{NAV_ICONS[name]} {name}",
            label_visibility="collapsed",
        )

        live = len(tournament.get_matches_by_status(MatchStatus.LIVE))
        played = len(tournament.finished_matches)
        rows = [
            f'<div class="n">{esc(tournament.name)}</div>',
            f"<div>{phase_pill(tournament.phase)}</div>",
            f'<div class="r"><span>Teams</span><b>{len(tournament.teams)}</b></div>',
            f'<div class="r"><span>Fixtures played</span><b>{played} / {len(tournament.matches)}</b></div>',
        ]
        if tournament.current_matchday:
            rows.append(
                f'<div class="r"><span>Matchday</span>'
                f"<b>{tournament.current_matchday} of {tournament.total_matchdays}</b></div>"
            )
        if live:
            rows.append(f'<div class="r"><span>Live now</span><b>{live}</b></div>')

        render('<div class="ea-season">' + "".join(rows) + "</div>")

    return page
