"""Small reusable HTML components (all user text is escaped)."""

from html import escape

import streamlit as st

from league import MatchStatus


def header(kicker, title, subtitle):
    st.markdown(
        f"""
        <div class="ea-kicker">{escape(kicker)}</div>
        <h1 class="ea-title">{escape(title)}</h1>
        <div class="ea-subtitle">{escape(subtitle)}</div>
        """,
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(
        f'<div class="ea-section">{escape(title)}</div>',
        unsafe_allow_html=True,
    )


def stat_card(label, value, note="SEASON OVERVIEW"):
    st.markdown(
        f"""
        <div class="ea-card">
          <div class="ea-card-label">{escape(str(label))}</div>
          <div class="ea-card-value">{escape(str(value))}</div>
          <div class="ea-card-note">{escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(status):
    css = {
        MatchStatus.LIVE: "ea-pill ea-pill-green",
        MatchStatus.FINISHED: "ea-pill",
        MatchStatus.UPCOMING: "ea-pill",
    }.get(status, "ea-pill")

    st.markdown(
        f'<span class="{css}">{escape(status.upper())}</span>',
        unsafe_allow_html=True,
    )


def scoreline(match, score_text):
    st.markdown(
        f"<div class='ea-scoreline'>{escape(match.team1.name)} &nbsp; "
        f"<span>{escape(score_text)}</span> &nbsp; "
        f"{escape(match.team2.name)}</div>",
        unsafe_allow_html=True,
    )


def right_muted(text):
    st.markdown(
        f"<div class='ea-right-muted'>{escape(text)}</div>",
        unsafe_allow_html=True,
    )


def muted(text):
    st.markdown(
        f"<span class='small-muted'>{escape(text)}</span>",
        unsafe_allow_html=True,
    )
