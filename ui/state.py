"""
Session state: the single Tournament instance, navigation, flash messages,
and a helper that turns domain exceptions into user-facing messages.
"""

import random

import streamlit as st

from league import Tournament
from ui.assets import init_assets_state
from ui.icons import NAV_ICONS

DEFAULT_TOURNAMENT_NAME = "Elite Arena League"

NAV_KEY = "nav"
PAGES = (
    "Dashboard",
    "Fixtures",
    "Standings",
    "Teams & Players",
    "History",
    "Tools",
    "Manage League",
)

# Exceptions the domain layer raises on invalid input / invalid state.
DOMAIN_ERRORS = (ValueError, TypeError, RuntimeError)


def init_state():
    if "tournament" not in st.session_state:
        st.session_state.tournament = Tournament(DEFAULT_TOURNAMENT_NAME)

    if "flash" not in st.session_state:
        st.session_state.flash = None

    if NAV_KEY not in st.session_state:
        st.session_state[NAV_KEY] = PAGES[0]

    if "rng" not in st.session_state:
        st.session_state.rng = random.Random()

    if "celebrated" not in st.session_state:
        st.session_state.celebrated = False

    init_assets_state()


def get_tournament():
    return st.session_state.tournament


def set_tournament(tournament):
    st.session_state.tournament = tournament
    st.session_state.celebrated = False


def get_rng():
    return st.session_state.rng


def celebrate_if_complete(tournament):
    """One balloon drop when the final whistle of the season goes."""
    if not tournament.is_complete:
        st.session_state.celebrated = False
        return

    if not st.session_state.celebrated:
        st.session_state.celebrated = True
        st.balloons()


# ---------------------------------------------------------------------- #
# Navigation
# ---------------------------------------------------------------------- #
def go_to(page):
    """on_click callback: switch the sidebar navigation to `page`."""
    st.session_state[NAV_KEY] = page


def nav_button(label, page, key, kind="secondary"):
    st.button(label, key=key, on_click=go_to, args=(page,), type=kind, icon=NAV_ICONS.get(page))


# ---------------------------------------------------------------------- #
# Flash messages (survive one st.rerun)
# ---------------------------------------------------------------------- #
def flash(kind, message):
    st.session_state.flash = (kind, message)


def show_flash():
    if not st.session_state.get("flash"):
        return

    kind, message = st.session_state.flash
    renderer = {
        "success": st.success,
        "error": st.error,
        "warning": st.warning,
    }.get(kind, st.info)

    renderer(message)
    st.session_state.flash = None


def run_action(action, success_message, error_prefix):
    """
    Execute a domain action from a button / form.

    - `action` is a zero-argument callable (usually a lambda).
    - `success_message` is a string, or a callable receiving the action result.
    - Domain errors become an error flash; the app always reruns afterwards.
    """
    try:
        result = action()
    except DOMAIN_ERRORS as exc:
        flash("error", f"{error_prefix}: {exc}")
    else:
        if callable(success_message):
            success_message = success_message(result)
        flash("success", success_message)

    st.rerun()
