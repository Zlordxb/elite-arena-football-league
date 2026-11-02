"""
Session state: the single Tournament instance, flash messages,
and a helper that turns domain exceptions into user-facing messages.
"""

import streamlit as st

from league import Tournament

DEFAULT_TOURNAMENT_NAME = "Elite Arena League"

# Exceptions the domain layer raises on invalid input / invalid state.
DOMAIN_ERRORS = (ValueError, TypeError, RuntimeError)


def init_state():
    if "tournament" not in st.session_state:
        st.session_state.tournament = Tournament(DEFAULT_TOURNAMENT_NAME)

    if "flash" not in st.session_state:
        st.session_state.flash = None


def get_tournament():
    return st.session_state.tournament


def set_tournament(tournament):
    st.session_state.tournament = tournament


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
