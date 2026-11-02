"""
ELITE ARENA — Streamlit entry point.

Run with:
    streamlit run streamlit_app.py

All league rules live in the `league` package; the pages in `ui/views`
only render state and forward user actions to it.
"""

import streamlit as st

from ui.sidebar import render_sidebar
from ui.state import get_tournament, init_state, show_flash
from ui.styles import inject_styles
from ui.views import dashboard, fixtures, manage, standings, teams

PAGES = {
    "Dashboard": dashboard.render,
    "Fixtures": fixtures.render,
    "Standings": standings.render,
    "Teams & Players": teams.render,
    "Manage League": manage.render,
}


def main():
    st.set_page_config(
        page_title="Elite Arena | Football League",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()
    init_state()

    tournament = get_tournament()
    page = render_sidebar(tournament, list(PAGES))

    show_flash()
    PAGES[page](tournament)


main()
